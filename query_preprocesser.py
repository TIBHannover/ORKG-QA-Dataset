from orkg import ORKG
from tqdm import tqdm
import click
import re

orkg = ORKG(host="http://orkg.org/orkg/", simcomp_host="http://orkg.org/orkg/simcomp/")

PRE_DEFINED_MAPPINGS = {
    'scope': 'P7047', 'rash': 'R8350', 'graph': 'P5008', 'dataset': 'P2005', 'aggregation': 'P5038',
    'evaluation': 'P34', 'precision': 'P3004', 'recall': 'P5015', 'fmeasure': 'P5016', 'implementation': 'P15',
    'metric': 'P2006', 'sample_size_n': 'P15687', 'location': 'P37537', 'has_software': 'P23031',
    'ontology': 'P7034', 'iri': 'P7042', 'cosine': 'R6006', 'evidence': 'P5004', 'indicator_for_well_being': 'P36089',
    'has_frequency': 'P37530', 'non_wheat_flour': 'P37571'
}


@click.command()
@click.option('-q', '--query', prompt='Query', help='Query to be preprocessed')
def parse(query):
    query = find_patterns(query, 'orkgp', orkg.predicates)
    query = find_patterns(query, 'orkgr', orkg.resources)
    print(query)


def find_patterns(query, prefix, client):
    # create regular expression to get all values of the pattern "orkgx:<value>"
    pattern = prefix + r':([^\s]+)'
    # get all values of the pattern
    values = re.findall(pattern, query)
    # iterate over all values
    for value in tqdm(values, desc=f"Handling {prefix}"):
        # check if the id exist in the ORKG
        if client.exists(value):
            continue
        else:
            # if not, look up by label
            clean_value = value.replace('_', ' ')
            if value in PRE_DEFINED_MAPPINGS:
                replace_with = PRE_DEFINED_MAPPINGS[value]
                query = query.replace(f'{prefix}:' + value, f'{prefix}:' + replace_with)
                # log that the value was replaced
                print(f"Replaced {value} with {replace_with} from pre-defined mapping")
                continue
            possible_labels = client.get(q=clean_value).content
            # if there is only one label, use it
            if len(possible_labels) == 1:
                # replace the value in the query with the id
                query = query.replace(f'{prefix}:' + value, f'{prefix}:' + possible_labels[0]['id'])
                # log that the value was replaced
                print(f"Replaced {value} with {possible_labels[0]['id']}")
            elif len(possible_labels) > 1:
                # if there are multiple labels, display a warning, but still choose the first one
                click.echo(
                    'Multiple labels found for {}:{}. Using {}'.format(prefix, value, possible_labels[0]['id']))
                query = query.replace(f'{prefix}:' + value, f'{prefix}:' + possible_labels[0]['id'])
                # log that the value was replaced
                print(f"Replaced {value} with {possible_labels[0]['id']}")
            else:
                # if there are no labels, display a error message, and leave it as it is
                click.echo('Error: No label found for {}:{}'.format(prefix, value))
                # log that the nothing was replaced
                print(f"No replacement for {value}")
    return query


if __name__ == '__main__':
    parse()
