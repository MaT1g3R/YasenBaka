import requests
import json


def calculate_coeff(region: str):
    """
    Get the coefficients used for WTR calculation and calculate the average 
    expected server wide
    :param region: the region 
    :return: a tuple of (coefficients, expected_average)
    :rtype: tuple
    """
    coeff_url = 'https://api.{}.warships.today/json/wows/' \
                'ratings/warships-today-rating/coefficients'.format(region)
    coeff_res = json.loads(requests.get(coeff_url).content)
    expected = coeff_res['expected']
    coefficients = coeff_res['coefficients']
    n = len(expected)
    expected_average = {}
    for d in expected:
        for key in d:
            if key not in expected_average:
                expected_average[key] = d[key]
            else:
                expected_average[key] += d[key]
    for key, val in expected_average.items():
        expected_average[key] = val/n
    return coefficients, expected_average


def coeff_all_region():
    """
    Get coefficients and expected average from all regions
    :return: a tuple of dictionaries, (coefficients, expected)
    :rtype: tuple
    """
    coefficients = {}
    expected = {}
    na = calculate_coeff('na')
    coefficients['na'] = na[0]
    expected['na'] = na[1]

    eu = calculate_coeff('eu')
    coefficients['eu'] = eu[0]
    expected['eu'] = eu[1]

    asia = calculate_coeff('asia')
    coefficients['asia'] = asia[0]
    expected['asia'] = asia[1]

    ru = calculate_coeff('ru')
    coefficients['ru'] = ru[0]
    expected['ru'] = ru[1]

    return coefficients, expected
