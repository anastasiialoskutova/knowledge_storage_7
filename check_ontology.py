from rdflib import Graph, RDF, OWL

g = Graph()
g.parse("models/onto.owl", format="turtle")

classes = set(g.subjects(RDF.type, OWL.Class))
object_properties = set(g.subjects(RDF.type, OWL.ObjectProperty))
data_properties = set(g.subjects(RDF.type, OWL.DatatypeProperty))

print("Ontology parsed successfully")
print("Classes:", len(classes))
print("Object properties:", len(object_properties))
print("Data properties:", len(data_properties))
print("Triples:", len(g))