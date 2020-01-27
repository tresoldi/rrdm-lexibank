import attr
import csv
import json
from clldutils.misc import slug
from clldutils.path import Path
from pylexibank import Concept
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar


def build_concept_id(concept):
    """
    Build a concept id in the format `number_gloss`.

    The gloss is simplified to lowercase, with no extended/accented
    letters, and no spaces. We use the Concepticon gloss by default,
    using the original name only if the concept is not mapped.
    """

    # If we have a concepticon gloss, use it; otherwise, use the name
    # stripped of all additional information.
    if concept.concepticon_gloss:
        gloss = concept.concepticon_gloss
    else:
        gloss = (concept.name.split("::")[0],)

    return "%s_%s" % (concept.id.split("_")[0], slug(gloss))


class Dataset(BaseDataset):
    """
    Class defining our dataset.
    """

    # Sets the working `dir`ectory and the dataset `id`
    dir = Path(__file__).parent
    id = "rrdm"

    def cmd_makecldf(self, args):
        """
        Method for reading raw data, auxiliary data, and writing CLDF files.
        """

        # Add bibliographic sources
        args.writer.add_sources()

        # Add languages
        languages = args.writer.add_languages(lookup_factory="Name")

        # add concepts
        concepts = args.writer.add_concepts(
            id_factory=lambda x: build_concept_id(x), lookup_factory="Name"
        )

        # Load raw data and add forms
        with open("raw/dataset.csv") as raw_data:
            # Read the raw data as a list of dictionaries
            reader = csv.DictReader(raw_data)

            # Iterate over each entry and add it; note that, as we lack the
            # difference between values and forms in these mock datasets, we
            # use the raw value for both fields.
            for entry in reader:
                # If the segments are given in the raw source, hand-coded,
                # make a list out of them and call the appropriate function;
                # otherwise, call the default ones that accepts no segments.
                if entry['Segments']:
                    args.writer.add_form_with_segments(
                        Language_ID=languages[entry["Language"]],
                        Parameter_ID=concepts[entry["Concept"]],
                        Value=entry["Value"],
                        Form=entry["Value"],
                        Segments=entry['Segments'].split(),
                        Source=["Dellert2017"],
                    )
                else:
                    args.writer.add_form(
                        Language_ID=languages[entry["Language"]],
                        Parameter_ID=concepts[entry["Concept"]],
                        Value=entry["Value"],
                        Form=entry["Value"],
                        Source=["Dellert2017"],
                    )
