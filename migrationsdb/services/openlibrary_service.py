from typing import Optional

import requests
from django.core.cache import cache

"""
Servicio para buscar libros en Open Library (https://openlibrary.org/developers/api).
Usa la API pública sin autenticación.
"""
BASE_URL = "https://openlibrary.org"
TIMEOUT = 10
CACHE_TTL = 600  # segundos


def _get_json(url: str, params: Optional[dict] = None):
    """
    Realiza una petición GET y retorna el JSON decodificado.
    Lanza excepción si hay error de red o HTTP.
    :param url: URL completa
    :param params: parámetros query
    :return: dict con JSON decodificado
    """
    params = params or {}
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _pick_isbn(doc) -> Optional[str]:
    """
    Dado un documento de Open Library, retorna el ISBN a usar (priorizando ISBN13).
    :param doc: dict con datos del libro
    :return: ISBN o None
    """
    isbns = doc.get("isbn") or []
    # Priorizar ISBN13
    for v in isbns:
        s = str(v).replace("-", "").upper().strip()
        if len(s) == 13 and s.isdigit():
            return s
    # Luego ISBN10 (permitiendo dígito de control X)
    for v in isbns:
        s = str(v).replace("-", "").upper().strip()
        if len(s) == 10 and s[:-1].isdigit() and (s[-1].isdigit() or s[-1] == "X"):
            return s
    return None


def _cover_url(doc, isbn: Optional[str]):
    cover_id = doc.get("cover_i")
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    if isbn:
        return f"https://covers.openlibrary.org/b/ISBN/{isbn}-M.jpg"
    return None


def search_books(q: str, page: int = 1, page_size: int = 20):
    """
    Busca libros en Open Library y devuelve:
    {items: [{title, authors, year, isbn, pages, subjects, cover_url}], page, next, prev, total}
    :param q: término de búsqueda
    :param page: página (1..N)
    :param page_size: tamaño de página (1..100)
    :return: dict con resultados y paginación
    """

    # Validar y limpiar entrada
    q = (q or "").strip()
    if not q:
        return {"items": [], "page": 1, "next": None, "prev": None, "total": 0}

    # Validar y limitar paginación
    page = max(1, int(page or 1))
    page_size = max(1, min(100, int(page_size or 20)))
    cache_key = f"ol:search:{q}:{page}:{page_size}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {"q": q, "page": page, "limit": page_size}
    data = _get_json(f"{BASE_URL}/search.json", params=params)

    items = []
    for d in data.get("docs", []):
        picked = _pick_isbn(d)
        item = {
            "title": d.get("title") or "",
            "authors": d.get("author_name") or [],
            "year": d.get("first_publish_year") or None,
            "isbn": picked,
            "pages": d.get("number_of_pages_median") or None,
            "subjects": d.get("subject") or [],
            "cover_url": _cover_url(d, picked),
        }
        items.append(item)

    total = int(data.get("numFound", 0) or 0)
    next_page = page + 1 if (page * page_size) < total else None
    prev_page = page - 1 if page > 1 else None

    result = {"items": items, "page": page, "next": next_page, "prev": prev_page, "total": total}
    cache.set(cache_key, result, CACHE_TTL)
    return result


def get_book_by_isbn(isbn: str):
    """
    Obtiene datos del primer resultado por ISBN.
    :param isbn: ISBN10 o ISBN13 (con o sin guiones)
    :return: {title, authors, year, isbn, pages, subjects, cover_url} o None.
    """

    # Manejar casos especiales sin ISBN
    if not isbn or isbn == 'no-isbn':
        return None

    # Validar y limpiar entrada
    isbn_clean= (isbn or "").replace("-", "").strip()
    if not isbn_clean:
        return None

    # Obtener información del caché
    cache_key = f"ol:isbn:{isbn_clean}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Buscar en Open Library
    data = _get_json(f"{BASE_URL}/search.json", params={"isbn": isbn, "limit": 1})
    docs = data.get("docs") or []
    if not docs:
        return None

    d = docs[0]
    picked = _pick_isbn(d) or isbn
    book = {
        "title": d.get("title") or "",
        "authors": d.get("author_name") or [],
        "year": d.get("first_publish_year") or None,
        "isbn": picked,
        "pages": d.get("number_of_pages_median") or None,
        "subjects": d.get("subject") or [],
        "cover_url": _cover_url(d, picked),
    }
    cache.set(cache_key, book, CACHE_TTL)
    return book