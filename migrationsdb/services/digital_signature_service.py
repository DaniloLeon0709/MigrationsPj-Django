import io
import os
import traceback
from datetime import datetime, timedelta, timezone

from django.conf import settings
from pyhanko.sign import signers, fields
from pyhanko.pdf_utils import incremental_writer

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption

from asn1crypto import x509 as asn1_x509
from asn1crypto import keys as asn1_keys
from pyhanko_certvalidator.registry import CertificateRegistry


class DigitalSignatureService:
    """
    Servicio para firmar digitalmente PDF's.
    Usa pyHanko y cryptography.
    Configuración opcional en settings.py:
    - DIGITAL_CERT_PATH: ruta a certificado PKCS#12 (*.p12/*.pfx) o PEM (*.pem/*.crt)
    - PRIVATE_KEY_PATH: ruta a clave privada PEM (*.pem/*.key), si el cert no es PKCS#12
    - CERT_PASSWORD: contraseña del certificado/clave, si aplica
    Si no hay configuración válida, usa un certificado autofirmado temporal para pruebas.
    """

    def __init__(self):
        self.cert_path = getattr(settings, 'DIGITAL_CERT_PATH', None)
        self.private_key_path = getattr(settings, 'PRIVATE_KEY_PATH', None)
        self.cert_password = getattr(settings, 'CERT_PASSWORD', None)

    def create_self_signed_cert(self):
        """
        Crea un certificado autofirmado para pruebas.
        :return: (private_key, certificate) ambos como objetos de cryptography
        """

        # Generar clave privada RSA
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Crear certificado autofirmado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Madrid"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Madrid"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Biblioteca Personal"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Sistema Biblioteca"),
        ])

        # Fechas de validez
        now = datetime.now(timezone.utc)
        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=30))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    key_cert_sign=False,
                    crl_sign=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            .add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CODE_SIGNING]),
                critical=False
            )
        )
        # Firmar el certificado
        cert = builder.sign(private_key, hashes.SHA256())
        return private_key, cert

    def _load_signer_from_files(self):
        """
        Intenta cargar un signer desde archivos configurados en settings:
        - PKCS#12 (*.p12/*.pfx) o par cert+key PEM.
        :return: SimpleSigner o None si no se pudo cargar
        """

        # Validar ruta de certificado
        if not self.cert_path or not os.path.exists(self.cert_path):
            return None

        # Preparar contraseña si aplica
        passphrase = (
            self.cert_password.encode('utf-8')
            if isinstance(self.cert_password, str) and self.cert_password
            else self.cert_password
        )

        # Intentar cargar el signer
        try:
            # Cargar PKCS#12 si aplica
            if self.cert_path.lower().endswith(('.p12', '.pfx')):
                return signers.SimpleSigner.load_pkcs12(self.cert_path, passphrase=passphrase)

            # Cargar par PEM
            if not self.private_key_path or not os.path.exists(self.private_key_path):
                return None

            # Cargar desde archivos PEM
            return signers.SimpleSigner.load(
                cert_file=self.cert_path,
                key_file=self.private_key_path,
                passphrase=passphrase
            )
        except Exception as e:
            traceback.print_exc()
            return None

    def get_signer(self):
        """
        Obtiene un SimpleSigner válido, ya sea desde archivos o creando uno autofirmado.
        :return: SimpleSigner listo para usar
        """

        # Intentar cargar desde archivos configurados
        signer = self._load_signer_from_files()
        if signer:
            return signer

        # Certificado autofirmado
        private_key, cert = self.create_self_signed_cert()
        try:
            # Convertir a asn1crypto para pyHanko
            asn1_cert = asn1_x509.Certificate.load(cert.public_bytes(Encoding.DER))
            pkcs8_der = private_key.private_bytes(
                encoding=Encoding.DER,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )
            asn1_priv = asn1_keys.PrivateKeyInfo.load(pkcs8_der)

            # Crear SimpleSigner
            cert_registry = CertificateRegistry()
            signer = signers.SimpleSigner(
                signing_cert=asn1_cert,
                signing_key=asn1_priv,
                cert_registry=cert_registry
            )
            return signer
        except Exception as e:
            traceback.print_exc()
            raise

    def sign_pdf(self, pdf_bytes, reason="Documento generado automáticamente",
                 location="Sistema Biblioteca", add_visual_signature=True):
        """
        Firma el PDF (saneando encabezado si es necesario) y devuelve los bytes firmados.
        :param pdf_bytes: bytes del PDF a firmar
        :param reason: motivo de la firma
        :param location: ubicación de la firma
        :param add_visual_signature: si True, agrega una firma visual en la página 0
        :return: bytes del PDF firmado, o los originales si hubo error
        """
        try:
            # Validar bytes de entrada
            if not pdf_bytes:
                print("[DigitalSignatureService] pdf_bytes vacío, no se puede firmar.")
                return pdf_bytes

            # Buscar el inicio del PDF
            idx = pdf_bytes.find(b'%PDF-')
            if idx == -1:
                return pdf_bytes
            if idx > 0:
                pdf_bytes = pdf_bytes[idx:]

            # Preparar writer incremental
            input_stream = io.BytesIO(pdf_bytes)
            writer = incremental_writer.IncrementalPdfFileWriter(input_stream)

            # Obtener signer
            signer = self.get_signer()

            # Configurar metadata de la firma
            meta = signers.PdfSignatureMetadata(
                field_name='BibliotecaPersonalSignature',
                reason=reason,
                location=location,
            )

            # Firmar con o sin firma visual
            if add_visual_signature:
                sig_field_spec = fields.SigFieldSpec(
                    sig_field_name='BibliotecaPersonalSignature',
                    on_page=0,
                    box=(400, 50, 550, 120)
                )
                out = signers.sign_pdf(writer, meta, signer=signer, new_field_spec=sig_field_spec)
            else:
                out = signers.sign_pdf(writer, meta, signer=signer)

            result = out.getvalue()
            delta = len(result) - len(pdf_bytes)
            return result

        except Exception as e:
            traceback.print_exc()
            return pdf_bytes