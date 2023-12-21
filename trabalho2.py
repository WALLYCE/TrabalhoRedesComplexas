from owlready2 import *
import networkx as nx
import matplotlib.pyplot as plt
import community

# Carregue a ontologia
onto = get_ontology("ontologyCompleted.rdf").load()

# Crie um grafo ponderado
G = nx.Graph()

# Adicione nós ao grafo (alunos) com as propriedades específicas como atributos
Student = onto.Student
for student_instance_1 in Student.instances():
    student_id_1 = student_instance_1.label.first()

    # Verifique se a string "ATI" não está presente no rótulo do estudante 1
    if student_instance_1.StudentHasStatus.__class__.__name__ != 'Active':
        for student_instance_2 in Student.instances():
            student_id_2 = student_instance_2.label.first()

            # Verifique se os estudantes são diferentes e se a string "ATI" não está presente no rótulo do estudante 2
            if student_id_1 != student_id_2 and student_instance_2.StudentHasStatus.__class__.__name__ != 'Active':
                # Calcule a diferença inversa dos GPAs como peso
                gpa_1 = student_instance_1.GPA
                gpa_2 = student_instance_2.GPA
                gpa_difference = 1 / (abs(gpa_1 - gpa_2) + 1)  # Adicionando 1 para evitar divisão por zero
                
                if(student_instance_1.StudentReceivedStudentAssistance.__class__.__name__ in student_instance_2.StudentReceivedStudentAssistance.__class__.__name__ ):
                    gpa_difference +=1;

                # Adicione a aresta com peso igual à diferença inversa dos GPAs
                G.add_edge(student_id_1, student_id_2, weight=gpa_difference)

# Use o algoritmo Louvain para detectar comunidades
partition = community.best_partition(G, weight='weight')

# Organize as comunidades em um dicionário
communities = {}
for node, community_id in partition.items():
    if community_id not in communities:
        communities[community_id] = {'CON': 0, 'EVA': 0}
    if 'CON' in node:
        communities[community_id]['CON'] += 1
    elif 'EVA' in node:
        communities[community_id]['EVA'] += 1

# Imprima as estatísticas das comunidades
for idx, community_stats in communities.items():
    total_nodes = community_stats['CON'] + community_stats['EVA']
    con_percentage = (community_stats['CON'] / total_nodes) * 100
    eva_percentage = (community_stats['EVA'] / total_nodes) * 100
    print(f'Comunidade {idx}: CON = {con_percentage:.2f}%, EVA = {eva_percentage:.2f}%')

# Desenhe o grafo com as cores das comunidades e o layout Fruchterman-Reingold
pos = nx.spring_layout(G, k=0.8)
colors = [partition[node] for node in G.nodes]

nx.draw_networkx(G, pos, node_color=colors, with_labels=True, alpha=0.8, cmap=plt.cm.viridis)
plt.show()
