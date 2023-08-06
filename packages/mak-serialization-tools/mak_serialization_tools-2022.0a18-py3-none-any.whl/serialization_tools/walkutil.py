from functools import partial
from os import PathLike
from os.path import splitext, join
from typing import Union, List, Tuple, Iterable, Callable, Optional

WhiteList = Union[List[str], str]
BlackList = WhiteList

OsWalkResult = Tuple[str, Iterable[str], Iterable[str]]
OsWalk = Iterable[OsWalkResult]

WalkPredicate = Callable[[str], bool]


def strict_whitelisted(value: str, whitelist: WhiteList):
    if not isinstance(whitelist, str):
        return value in whitelist
    else:
        return value == whitelist


def whitelisted(value: str, whitelist: WhiteList):
    if not isinstance(whitelist, str):
        for word in whitelist:
            if word in value:
                return True
        return False
    else:
        return whitelist in value


def strict_blacklisted(value: str, blacklist: BlackList):
    # These are functionally, the same
    #   how we use them differs greatly
    return strict_whitelisted(value, blacklist)


def blacklisted(value: str, blacklist: BlackList):
    # These are functionally, the same
    #   how we use them differs greatly
    return whitelisted(value, blacklist)


def __resolve_whitelist_blacklist_results(whitelist_result: Optional[bool], blacklist_result: Optional[bool]) -> bool:
    # If whitelist only
    #   Assume blacklist is remaining 'Universe'
    # If blacklist only
    #   Assume whitelist is remaining 'Universe'
    # If whitelist AND blacklist
    #   return whitelist_result or not blacklist_result

    if whitelist_result is not None and blacklist_result is not None:
        return whitelist_result or not blacklist_result
    elif whitelist_result is not None:
        return whitelist_result
    elif blacklist_result is not None:
        return not blacklist_result
    else:
        raise NotImplementedError


def file_extension_allowed(path: PathLike, whitelist: Optional[WhiteList] = None, blacklist: Optional[BlackList] = None) -> bool:
    _, extension = splitext(path)

    wl_result = strict_whitelisted(extension, whitelist) if whitelist else None
    bl_result = strict_blacklisted(extension, blacklist) if blacklist else None
    return __resolve_whitelist_blacklist_results(wl_result, bl_result)


def file_extension_allowed_predicate(whitelist: Optional[WhiteList] = None, blacklist: Optional[BlackList] = None) -> Optional[WalkPredicate]:
    if not whitelist and not blacklist:
        return None
    return partial(file_extension_allowed, whitelist=whitelist, blacklist=blacklist)


def filter_by_file_extension(walk: OsWalk, whitelist: Optional[WhiteList] = None, blacklist: Optional[BlackList] = None, **filter_kwargs) -> OsWalk:
    pred = file_extension_allowed_predicate(whitelist, blacklist)
    return filter_files_by_predicate(walk, pred, **filter_kwargs)


def path_allowed(path: Union[str,PathLike], whitelist: Optional[WhiteList] = None, blacklist: Optional[BlackList] = None) -> bool:
    if isinstance(path,PathLike):
        str_path = path.__fspath__()
    else:
        str_path = path
    wl_result = whitelisted(str_path, whitelist) if whitelist else None
    bl_result = blacklisted(str_path, blacklist) if blacklist else None
    return __resolve_whitelist_blacklist_results(wl_result, bl_result)


def path_allowed_predicate(whitelist: Optional[WhiteList] = None, blacklist: Optional[BlackList] = None) -> Optional[WalkPredicate]:
    if not whitelist and not blacklist:
        return None
    return partial(path_allowed, whitelist=whitelist, blacklist=blacklist)


def filter_by_path(walk: OsWalk, whitelist: Optional[WhiteList] = None, blacklist: Optional[BlackList] = None, **filter_kwargs) -> OsWalk:
    pred = path_allowed_predicate(whitelist, blacklist)
    return filter_by_predicate(walk, pred, **filter_kwargs)


def filter_files_by_predicate(walk: OsWalk, predicate: WalkPredicate, abs_path: bool = False) -> OsWalk:
    """
    Filters a walk's file collection using the given predicate.

    If a predicate was not provided, the original walk is returned.

    :param walk: The walk 'object' to filter
    :param predicate: The condition to check; should take in the file path/name and return a boolean
    :param abs_path: Use the absolute file path, instead of the basename
    """
    if not predicate:
        return walk

    for root, _, files in walk:
        if abs_path:
            valid = (f for f in files if predicate(join(root, f)))
        else:
            valid = (f for f in files if predicate(f))
        yield root, _, valid


def filter_folders_by_predicate(walk: OsWalk, predicate: WalkPredicate, abs_path: bool = False, prune: bool = False) -> OsWalk:
    """
    Filters a walk's folder collection using the given predicate.

    :param walk: The walk 'object' to filter
    :param predicate: The condition to check; should take in the folder path/name and return a boolean
    :param abs_path: Use the absolute folder path, instead of the basename
    :param prune: Modify folders in-place to avoid walking into subdirectories. This only works when os.walk is called with top-down=True (the default)
    """
    if not predicate:
        return walk

    for root, folders, _ in walk:
        if abs_path:
            valid = (f for f in folders if predicate(join(root, f)))
        else:
            valid = (f for f in folders if predicate(f))

        if prune:
            folders[:] = list(valid)
            valid = folders
        yield root, valid, _


def filter_by_predicate(walk: OsWalk, predicate: WalkPredicate, abs_path: bool = False, prune: bool = False) -> OsWalk:
    """
    Filters a walk's folder AND file collection using the given predicate.

    :param walk: The walk 'object' to filter
    :param predicate: The condition to check; should take in the folder/file path/name and return a boolean
    :param abs_path: Use the absolute folder/file path, instead of the basename
    :param prune: Modify folders in-place to avoid walking into subdirectories. This only works when os.walk is called with top-down=True (the default)
    """
    if not predicate:
        return walk

    for root, folders, files in walk:
        if abs_path:
            valid_folders = (f for f in folders if predicate(join(root, f)))
            valid_files = (f for f in files if predicate(join(root, f)))
        else:
            valid_folders = (f for f in folders if predicate(f))
            valid_files = (f for f in files if predicate(f))

        if prune:
            folders[:] = list(valid_folders)
            valid_folders = folders
        yield root, valid_folders, valid_files


def collapse_walk_on_files(walk: OsWalk, abs_path: bool = True) -> Iterable[str]:
    """Makes a walk only return an iterator for the file path."""
    for root, _, files in walk:
        for file in files:
            if abs_path:
                yield join(root, file)
            else:
                yield file
