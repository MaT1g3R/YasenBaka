from typing import Iterable

from minoshiro import Medium, Minoshiro, Site
from minoshiro.helpers import get_synonyms


class AnimeSearcher(Minoshiro):
    async def get(self, query: str, medium: Medium,
                  sites: Iterable[Site] = None, *, timeout=3):
        sites = sites if sites else list(Site)
        cached_data, cached_id = await self._get_cached(query, medium)
        to_be_cached = {}
        names = []
        return_val = {}
        for site in sites:
            res, id_ = await self._get_result(
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
        await super()._cache(to_be_cached, names, medium)
