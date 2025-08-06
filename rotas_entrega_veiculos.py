import random
import matplotlib.pyplot as plt

# Dados do problema
num_clientes = 10
num_veiculos = 3
capacidade_veiculo = 20

demandas = [7, 3, 7, 4, 6, 4, 7, 5, 8, 2]  # Demandas fixas

tempos_viagem = [
    [0, 10, 15, 20, 12, 18, 10, 14, 16, 19, 11],
    [10, 0, 8, 17, 9, 13, 11, 12, 15, 10, 14],
    [15, 8, 0, 12, 10, 16, 14, 9, 11, 13, 12],
    [20, 17, 12, 0, 15, 10, 18, 16, 14, 12, 19],
    [12, 9, 10, 15, 0, 11, 13, 17, 10, 16, 8],
    [18, 13, 16, 10, 11, 0, 12, 15, 14, 9, 17],
    [10, 11, 14, 18, 13, 12, 0, 10, 16, 15, 12],
    [14, 12, 9, 16, 17, 15, 10, 0, 11, 13, 14],
    [16, 15, 11, 14, 10, 14, 16, 11, 0, 12, 15],
    [19, 10, 13, 12, 16, 9, 15, 13, 12, 0, 11],
    [11, 14, 12, 19, 8, 17, 12, 14, 15, 11, 0]
]

# Parâmetros
tamanho_populacao = 20
num_geracoes = 50
taxa_mutacao = 0.2  # Aumentada para mais exploração

# Gerar cromossomo: cada cliente é atribuído a um veículo (0, 1 ou 2)
def gerar_cromossomo():
    if random.random() < 0.2:  # 20% balanceado
        cromossomo = [i % num_veiculos for i in range(num_clientes)]
        random.shuffle(cromossomo)
    else:
        cromossomo = [random.randint(0, num_veiculos - 1) for _ in range(num_clientes)]
    return cromossomo

# Calcular tempo de uma rota: depósito -> clientes -> depósito
def calcular_tempo_rota(clientes):
    if not clientes:
        return 0
    tempo = tempos_viagem[0][clientes[0]]  # Depósito ao primeiro cliente
    for i in range(len(clientes) - 1):
        tempo += tempos_viagem[clientes[i]][clientes[i + 1]]
    tempo += tempos_viagem[clientes[-1]][0]  # Último cliente ao depósito
    return tempo

# Calcula aptidão de um cromossomo (maior = melhor)
def calcular_aptidao(cromossomo):
    cargas = [0] * num_veiculos  # Carga inicial de cada veículo
    rotas = [[] for _ in range(num_veiculos)]  # Rotas de cada veículo
    for i, v in enumerate(cromossomo):  # Atribui clientes aos veículos
        cargas[v] += demandas[i]  # Soma demanda do cliente
        rotas[v].append(i + 1)  # Adiciona cliente à rota

    tempo_total = sum(calcular_tempo_rota(rota) for rota in rotas)  # Tempo total das rotas
    penalidade = sum(max(0, carga - capacidade_veiculo) for carga in cargas) * 1000  # Penaliza sobrecarga
    return 10000 / (tempo_total + penalidade) ** 2  # Aptidão: menor com sobrecarga
    # Exemplo: tempo_total = 150, sem sobrecarga → aptidão ≈ 0.444
    #          tempo_total = 150, sobrecarga de 5 → penalidade = 5000, aptidão ≈ 0.0004

# Seleção por torneio: escolhe o melhor de um grupo aleatório
def selecao_torneio(populacao, aptidoes, tamanho_torneio=3):
    torneio = random.sample(list(zip(populacao, aptidoes)), tamanho_torneio)  # Escolhe tamanho_torneio cromossomos aleatoriamente
    return max(torneio, key=lambda x: x[1])[0]  # Retorna o cromossomo com maior aptidão
    # Exemplo: escolhe 3 cromossomos, retorna o que tem maior aptidão

# Cruzamento de ponto único
def cruzamento(pai1, pai2):
    ponto = random.randint(1, len(pai1) - 1)
    filho1 = pai1[:ponto] + pai2[ponto:]
    filho2 = pai2[:ponto] + pai1[ponto:]
    return filho1, filho2

# Mutação: mudar até 2 clientes
def mutar(cromossomo):
    cromossomo = cromossomo[:]
    for _ in range(random.randint(1, 2)):
        if random.random() < taxa_mutacao:
            cliente = random.randint(0, len(cromossomo) - 1)
            cromossomo[cliente] = random.randint(0, num_veiculos - 1)
    return cromossomo

# Algoritmo genético
def algoritmo_genetico():
    populacao = [gerar_cromossomo() for _ in range(tamanho_populacao)]
    historico_tempo_total = []

    for geracao in range(num_geracoes):
      
        aptidoes = [calcular_aptidao(crom) for crom in populacao]
        melhor_aptidao = max(aptidoes)
        melhor_idx = aptidoes.index(melhor_aptidao)

        cargas = [0] * num_veiculos
        rotas = [[] for _ in range(num_veiculos)]

        for cliente, veiculo in enumerate(populacao[melhor_idx]):
            cargas[veiculo] += demandas[cliente]
            rotas[veiculo].append(cliente + 1)
        tempo_total = sum(calcular_tempo_rota(rota) for rota in rotas)

        historico_tempo_total.append(tempo_total)
        print(f"Geração {geracao}: Tempo total = {tempo_total:.2f}, Aptidão = {melhor_aptidao:.4f}")

        nova_populacao = [populacao[melhor_idx]]  # Elitismo
        while len(nova_populacao) < tamanho_populacao:
            pai1 = selecao_torneio(populacao, aptidoes)
            pai2 = selecao_torneio(populacao, aptidoes)
            filho1, filho2 = cruzamento(pai1, pai2)
            filho1 = mutar(filho1)
            filho2 = mutar(filho2)
            nova_populacao.extend([filho1, filho2])

        populacao = nova_populacao[:tamanho_populacao]

    # Melhor solução
    aptidoes = [calcular_aptidao(crom) for crom in populacao]
    melhor_idx = aptidoes.index(max(aptidoes))
    melhor_cromossomo = populacao[melhor_idx]
    
    cargas = [0] * num_veiculos
    rotas = [[] for _ in range(num_veiculos)]

    for cliente, veiculo in enumerate(melhor_cromossomo):
        cargas[veiculo] += demandas[cliente]
        rotas[veiculo].append(cliente + 1)
    tempo_total = sum(calcular_tempo_rota(rota) for rota in rotas)

    print("\nMelhor Solução:")
    print(f"Alocação: {melhor_cromossomo}")
    print(f"Demandas: {demandas}")
    print(f"Cargas: {cargas}")
    print(f"Rotas: {rotas}")
    print(f"Tempo total: {tempo_total:.2f}")
    print(f"Aptidão: {aptidoes[melhor_idx]:.4f}")

    plt.plot(range(num_geracoes), historico_tempo_total, label='Tempo Total', color='#1f77b4')
    plt.xlabel('Geração')
    plt.ylabel('Tempo Total (Minutos)')
    plt.title('Evolução do Tempo Total')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    random.seed(42)

    print("\nProfessor: Sérgio Polimante");
    print("    Aluno: Diego Ivan Mendes de Oliveira");

    print(f"\nDemandas dos clientes: {demandas}")
    print(f"Capacidade por veículo: {capacidade_veiculo} unidades")
    algoritmo_genetico()