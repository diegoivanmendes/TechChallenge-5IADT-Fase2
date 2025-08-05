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
taxa_mutacao = 0.3  # 

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

# Calcular aptidão: inverso do tempo total ao quadrado
def calcular_aptidao(cromossomo):
    cargas = [0] * num_veiculos
    rotas = [[] for _ in range(num_veiculos)]
    for cliente, veiculo in enumerate(cromossomo):
        cargas[veiculo] += demandas[cliente]
        rotas[veiculo].append(cliente + 1)

    # Reparo simples: mover clientes de veículos sobrecarregados
    while max(cargas) > capacidade_veiculo:
        veiculo_max = cargas.index(max(cargas))
        veiculo_min = cargas.index(min(cargas))
        clientes_max = [i for i, v in enumerate(cromossomo) if v == veiculo_max]
        if clientes_max:
            cliente = random.choice(clientes_max)
            cromossomo[cliente] = veiculo_min
            cargas[veiculo_max] -= demandas[cliente]
            cargas[veiculo_min] += demandas[cliente]
            rotas[veiculo_max].remove(cliente + 1)
            rotas[veiculo_min].append(cliente + 1)

    tempo_total = sum(calcular_tempo_rota(rota) for rota in rotas)
    return 10000 / (tempo_total ** 2)  # Amplifica diferenças

# Seleção por roleta: maior aptidão tem mais chance
def selecao_roleta(populacao, aptidoes):
    total_aptidao = sum(aptidoes)
    pick = random.uniform(0, total_aptidao)
    atual = 0
    for cromossomo, aptidao in zip(populacao, aptidoes):
        atual += aptidao
        if atual >= pick:
            return cromossomo
    return random.choice(populacao)  # Fallback

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
            pai1 = selecao_roleta(populacao, aptidoes)
            pai2 = selecao_roleta(populacao, aptidoes)
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
    print(f"Demandas dos clientes: {demandas}")
    print(f"Capacidade por veículo: {capacidade_veiculo} unidades")
    algoritmo_genetico()