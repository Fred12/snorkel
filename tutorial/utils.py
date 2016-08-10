import lxml.etree as et
from snorkel.models import CandidateSet
from snorkel.candidates import TemporarySpan


def collect_pubtator_annotations(doc, sents, sep=" "):
    """
    Given a Document with PubTator/CDR annotations, and a corresponding set of Sentences,
    extract a set of Ngram objects indexed according to **Sentence character indexing**
    NOTE: Assume the sentences are provided in correct order & have standard separator.
    """
    sent_offsets = [s.char_offsets[0] for s in sents]

    # Get Ngrams
    ngrams = CandidateSet()
    annotations = et.fromstring(doc.attribs['root']).xpath('.//annotation')
    for a in annotations:

        # Relation annotations
        if len(a.xpath('./infon[@key="relation"]')) > 0:

            # TODO: Pull these out!
            type = a.xpath('./infon[@key="relation"]/text()')[0]
            types = a.xpath('./infon[@key != "relation"]/@key')
            mesh_ids = a.xpath('./infon[@key != "relation"]/text()')
            pass

        # Mention annotations
        else:

            # NOTE: Ignore CompositeRole individual mention annotations for now
            comp_roles = a.xpath('./infon[@key="CompositeRole"]/text()')
            comp_role = comp_roles[0] if len(comp_roles) > 0 else None
            if comp_role == 'IndividualMention':
                continue

            # Get basic annotation attributes
            txt = a.xpath('./text/text()')[0]
            offset = int(a.xpath('./location/@offset')[0])
            length = int(a.xpath('./location/@length')[0])
            type = a.xpath('./infon[@key="type"]/text()')[0]
            mesh = a.xpath('./infon[@key="MESH"]/text()')[0]
            
            # Get sentence id and relative character offset
            si = len(sent_offsets) - 1
            for i,so in enumerate(sent_offsets):
                if offset == so:
                    si = i
                    break
                elif offset < so:
                    si = i - 1
                    break
            ngrams.append(TemporarySpan(char_start=offset, char_end=offset + length - 1, context=sents[si], meta={
                'mesh_id': mesh, 'type': type, 'composite': comp_role}))
    return ngrams