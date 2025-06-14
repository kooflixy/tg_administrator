def is_page_exists(page: int, lst: list) -> bool:
    '''Проверка на то что страница существует(если она не единственная)'''
    if page == 1 or lst:
        return False
    return True