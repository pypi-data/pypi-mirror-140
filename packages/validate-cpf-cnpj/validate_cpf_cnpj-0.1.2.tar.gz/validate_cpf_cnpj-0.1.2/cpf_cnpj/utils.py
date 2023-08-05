def cleaning(document: str) -> str:
    """Clean a given document

    Args:
        document (str): A CPF or CNPJ with special chars

    Returns:
        str: the document without special chars
    """
    return document.replace('-', '').replace('.', '').replace('/', '')
