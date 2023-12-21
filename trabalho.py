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
                
                # Adicione a aresta com peso igual à diferença inversa dos GPAs
                G.add_edge(student_id_1, student_id_2, weight=gpa_difference)

                # Adicione as informações do nó apenas se ainda não existirem
                if 'gender' not in G.nodes[student_id_1]:
                    G.nodes[student_id_1]['gender'] = student_instance_1.StudentHasGender.__class__.__name__
                if 'academic_assistance' not in G.nodes[student_id_1]:
                    G.nodes[student_id_1]['academic_assistance'] = student_instance_1.StudentReceivedStudentAssistance.__class__.__name__
                if 'admission_type' not in G.nodes[student_id_1]:
                    G.nodes[student_id_1]['admission_type'] = student_instance_1.StudentHasAdmissionType.__class__.__name__
                if 'nativity' not in G.nodes[student_id_1]:
                    G.nodes[student_id_1]['nativity'] = student_instance_1.StudentHasNativity.__class__.__name__
                if 'ethnicity' not in G.nodes[student_id_1]:
                    G.nodes[student_id_1]['ethnicity'] = student_instance_1.StudentHasEthnicity.__class__.__name__

                if 'gender' not in G.nodes[student_id_2]:
                    G.nodes[student_id_2]['gender'] = student_instance_2.StudentHasGender.__class__.__name__
                if 'academic_assistance' not in G.nodes[student_id_2]:
                    G.nodes[student_id_2]['academic_assistance'] = student_instance_2.StudentReceivedStudentAssistance.__class__.__name__
                if 'admission_type' not in G.nodes[student_id_2]:
                    G.nodes[student_id_2]['admission_type'] = student_instance_2.StudentHasAdmissionType.__class__.__name__
                if 'nativity' not in G.nodes[student_id_2]:
                    G.nodes[student_id_2]['nativity'] = student_instance_2.StudentHasNativity.__class__.__name__
                if 'ethnicity' not in G.nodes[student_id_2]:
                    G.nodes[student_id_2]['ethnicity'] = student_instance_2.StudentHasEthnicity.__class__.__name__

# Use o algoritmo Louvain para detectar comunidades
partition = community.best_partition(G, weight='weight')

# Organize as comunidades em um dicionário
communities = {}
for node, community_id in partition.items():
    if community_id not in communities:
        communities[community_id] = {'CON': [], 'EVA': []}
    if 'CON' in node:
        communities[community_id]['CON'].append(node)
    elif 'EVA' in node:
        communities[community_id]['EVA'].append(node)

# Contagem de tipos de gender e outras informações em cada comunidade
for idx, community_nodes in communities.items():
    total_nodes = len(community_nodes['CON']) + len(community_nodes['EVA'])
    con_percentage = (len(community_nodes['CON']) / total_nodes) * 100
    eva_percentage = (len(community_nodes['EVA']) / total_nodes) * 100
    
    # Dicionários para armazenar a contagem de cada atributo em cada comunidade
    attribute_counts = {'CON': {}, 'EVA': {}}
    
    # Percorra os nós "CON" da comunidade atual
    for node in community_nodes['CON']:
        # Obtenha os atributos do nó
        attr = G.nodes[node]
        for key, value in attr.items():
            if key not in attribute_counts['CON']:
                attribute_counts['CON'][key] = {}
            if value not in attribute_counts['CON'][key]:
                attribute_counts['CON'][key][value] = 1
            else:
                attribute_counts['CON'][key][value] += 1

    # Percorra os nós "EVA" da comunidade atual
    for node in community_nodes['EVA']:
        # Obtenha os atributos do nó
        attr = G.nodes[node]
        for key, value in attr.items():
            if key not in attribute_counts['EVA']:
                attribute_counts['EVA'][key] = {}
            if value not in attribute_counts['EVA'][key]:
                attribute_counts['EVA'][key][value] = 1
            else:
                attribute_counts['EVA'][key][value] += 1

    # Calcule as porcentagens para cada atributo em "CON"
    attribute_percentages_CON = {key: {subkey: (count / len(community_nodes['CON'])) * 100 for subkey, count in value.items()} for key, value in attribute_counts['CON'].items()}
    
    # Calcule as porcentagens para cada atributo em "EVA"
    attribute_percentages_EVA = {key: {subkey: (count / len(community_nodes['EVA'])) * 100 for subkey, count in value.items()} for key, value in attribute_counts['EVA'].items()}
    
    # Imprima as informações
    print(f'Comunidade {idx}: CON = {round(con_percentage, 2)}%, EVA = {round(eva_percentage, 2)}%')
    print('CON:')
    for attribute, percentages in attribute_percentages_CON.items():
        rounded_percentages = {key: round(value, 2) for key, value in percentages.items()}
        print(f'  {attribute}: {rounded_percentages}')

    print('EVA:')
    for attribute, percentages in attribute_percentages_EVA.items():
        rounded_percentages = {key: round(value, 2) for key, value in percentages.items()}
        print(f'  {attribute}: {rounded_percentages}')
    print('\n')
# Desenhe o grafo com as cores das comunidades e o layout Fruchterman-Reingold
pos = nx.spring_layout(G, k=0.8)
colors = [partition[node] for node in G.nodes]

nx.draw_networkx(G, pos, node_color=colors, with_labels=True, alpha=0.8, cmap=plt.cm.viridis)
plt.show()
