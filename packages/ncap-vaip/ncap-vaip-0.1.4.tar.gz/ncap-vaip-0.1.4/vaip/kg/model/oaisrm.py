import rdflib
from rdflib.namespace import XSD
from vaip.utilities.rdf_helper import is_valid_uri
from vaip.utilities.json_helper import find_and_fill_placeholders


class Oaisrm:
    """
    Class use to build knowgledge graph using OAIS Reference Model an VAIP ontology.
    """
    def __init__(self, vaip_prefix):
        """
        Initialize class by constructing a base knowledge graph.
        """
        self.namespaces = {
            "vaip": rdflib.Namespace(vaip_prefix)
        }
        self.kg = self.build_vaip_knowledge_graph()
        self.vaip_prefix = vaip_prefix

    def build_vaip_knowledge_graph(self):
        kg = rdflib.Graph()
        for prefix, ns in self.namespaces.items():
            kg.namespace_manager.bind(prefix, ns)

        return kg

    def save_rdf(self, path, format="application/rdf+xml"):
        self.kg.serialize(destination=path, format=format, encoding="utf-8")

    def save_rdf_text(self, format="application/rdf+xml"):
        return self.kg.serialize(destination=None, format=format, encoding="utf-8").decode("utf-8")

    def load_rdf(self, path, format="application/rdf+xml"):
        self.kg.parse(path, format=format)
        return self.kg

    def load_rdf_text(self, data, format="application/rdf+xml"):
        self.kg.parse(data=data, format=format)
        return self.kg

    def add(self, s, p, o):
        obj = None
        if not is_valid_uri(o):
            obj = rdflib.Literal(o)
        else:
            obj = rdflib.URIRef(o)
        self.kg.add((rdflib.URIRef(s), rdflib.URIRef(p), obj))
        return self

    def copy_query_results_to_new_graph(self, rows, original_root_iri, id_prefix, id_suffix):
        """ 
        Loop through the query result rows and build a map of old_id -> new_id, where
        id in this case refers to the string segment after the final trailing slash of our IRI
        eg. http://uri.of.thing/entities/{thing_id}
    
        We then format each row as a string in n-triple format, and finally join this
        list of triples and replace all the old_ids with new_ids contained in the iri_map.
        """
        self.kg = self.build_vaip_knowledge_graph()

        iri_map = {}
        new_triples = []
        for row in rows:
            subject = row[0]
            predicate = row[1]
            obj = row[2]
            subj_prefix, subj_id = subject.rsplit("/", 1)
            if subject not in iri_map:
                new_id = f"{id_prefix}{subj_id}{id_suffix}"
                iri_map[str(subject)] = f"{subj_prefix}/{new_id}"

            new_obj = None
            if isinstance(obj, rdflib.URIRef):
                new_obj = f"<{str(obj)}>"
            elif isinstance(obj, rdflib.Literal):
                new_obj = f'"{str(obj)}"'
            new_triples.append(f"<{str(subject)}> <{str(predicate)}> {new_obj} .")
        
        nt_triples = "\n".join(new_triples)
        for k, v in iri_map.items():
            nt_triples = nt_triples.replace(k, v)
        
        self.load_rdf_text(data=nt_triples, format="nt")
        return iri_map[original_root_iri]

    def replace_placeholders_in_graph(self, placeholder_rows, incoming_payload):
        output = {}
        for row in placeholder_rows:
            key = str(row[0])
            value = str(row[1])
            output[key] = value
        
        filled = find_and_fill_placeholders(output, incoming_payload)
        for iri, v in filled.items():
            self.kg.set((rdflib.URIRef(iri), self.namespaces["vaip"].hasBits, rdflib.Literal(v, datatype=XSD.string)))
        return self

    # TODO: Either find a way to handle placeholders during the copying process, or
    # create a new utility file that contains SPARQL queries, so these queries can be shared with NeptuneClient
    def compose_find_placeholder_sparql(self, root_iri, graph_name):
        start_iri = f"<{root_iri}>" if root_iri is not None else "?x"
        from_clause = f"FROM <{graph_name}>" if graph_name is not None else ""

        sparql = f"""
        PREFIX vaip: <{self.vaip_prefix}>
        SELECT ?s ?o
        {from_clause}
        WHERE {{
            {start_iri} (rdf:|!rdf:)+ ?s .
            ?s vaip:hasBits ?o .
            FILTER (isLiteral(?o) && regex(?o, "^{{{{.*}}}}$"))
        }}
        """
        return sparql

    def retrieve_placeholders(self, root_iri, graph_name):
        sparql = self.compose_find_placeholder_sparql(root_iri, graph_name)

        result = self.kg.query(sparql)
        return result

    def build_aiu(self, rows, original_root_iri, id_prefix, id_suffix, incoming_payload):
        # Clone it
        new_root_iri = self.copy_query_results_to_new_graph(rows, original_root_iri, id_prefix=id_prefix, id_suffix=id_suffix)

        # Fill out placeholders
        placeholder_result = self.retrieve_placeholders(new_root_iri, graph_name=None)
        self.replace_placeholders_in_graph(placeholder_result, incoming_payload)

        return new_root_iri
