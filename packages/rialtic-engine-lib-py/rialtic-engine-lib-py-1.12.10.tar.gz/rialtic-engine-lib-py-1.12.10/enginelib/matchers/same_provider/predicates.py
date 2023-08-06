from enginelib.rds.provider_taxonomy_crosswalk import ProviderTaxonomyCrosswalk


def valid_taxonomy_code(code: str) -> bool:
    return ProviderTaxonomyCrosswalk.is_taxonomy_code_valid(code)


def match_taxonomy_codes(code1: str, code2: str) -> bool:
    specialties1 = ProviderTaxonomyCrosswalk.get_taxonomy_groups(code1)
    specialties2 = ProviderTaxonomyCrosswalk.get_taxonomy_groups(code2)
    return not specialties1.isdisjoint(specialties2)
