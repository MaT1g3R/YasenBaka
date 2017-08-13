from itertools import chain
from typing import Iterable

from minoshiro import Medium, Minoshiro, Site
from minoshiro.helpers import get_synonyms


class AnimeSearcher(Minoshiro):
    async def get(self, query: str, medium: Medium,
                  sites: Iterable[Site] = None, *, timeout=3):
        sites = sites if sites else list(Site)
        cached_data, cached_id = await self.__get_cached(query, medium)
        to_be_cached = {}
        names = []
        return_val = {}
        for site in sites:
            res, id_ = await self.__get_result(
                cached_data, cached_id, query, names, site, medium, timeout
            )
            if res:
                return_val[site] = res
                for title in get_synonyms(res, site):
                    names.append(title)
            if id_:
                to_be_cached[site] = id_
        return return_val, to_be_cached, names, medium

    async def cache(self, to_be_cached, names, medium):
        """
        Cache search results into the db.
        :param to_be_cached: items to be cached.
        :param names: all names for the item.
        :param medium: the medium type.
        """
        itere = set(chain(*names))
        for site, id_ in to_be_cached.items():
            await self.cache_one(site, id_, medium, itere)

    async def cache_one(self, site, id_, medium, iterator):
        """
        Cache one id.
        :param site: the site.
        :param id_: the id.
        :param medium: the medium type.
        :param iterator: an iterator for all names.
        """
        for name in iterator:
            if name:
                await self.db_controller.set_identifier(
                    name, medium, site, id_
                )
