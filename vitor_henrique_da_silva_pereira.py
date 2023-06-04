from enum import Enum

# STEP1 - CONFIGS (INCLUDE ERRORS)
class Configs(Enum):
    MAX_TAB_X = 15
    MAX_TAB_Y = 15
    MAX_TORP_QTT = 25
    BOATS_ID = ('1','2','3','4')
    TORPEDO_ID = "T"
    VALID_COLUMNS = ("A","B","C","D","E","F","G","H","I","J","L","M","N","O","P")

boats = {
    "1": {
        "max_posicoes": 4,
        "qtty": 5
    },
    "2": {
        "max_posicoes": 5,
        "qtty": 2
    },
    "3": {
        "max_posicoes": 1,
        "qtty": 10
    },
    "4": {
        "max_posicoes": 2,
        "qtty": 5
    }
}
class Encouracado(Enum):
    CODIGO = 1
    NOME = "Encouracado"
    MAX_POSICOES = 4
    QTTY = 5
class PortaAvioes(Enum):
    CODIGO = 2
    NOME = "PortaAvioes"
    MAX_POSICOES = 5
    QTTY = 2
class Submarinos(Enum):
    CODIGO = 3
    NOME = "Submarinos"
    MAX_POSICOES = 1
    QTTY = 10
class Cruzadores(Enum):
    CODIGO = 4
    NOME = "Cruzadores"
    MAX_POSICOES = 2
    QTTY = 5

class Error(Enum):
    NR_PART = 'ERROR_NR_PARTS_VALIDATION'
    OVW_PIECE = 'ERROR_OVERWRITE_PIECES_VALIDATION'
    POS_NOEXIST = 'ERROR_POSITION_NONEXISTENT_VALIDATION'


# STEP2 - RECEBER ARQUIVOS
def receber_arquivo(arquivo: str) -> str:
    return open(arquivo, 'r').readlines()

# STEP3 - CONFIGURAR TEMPLATE DO ARQUIVO <codigo>;<posicao><direcao> - <codigo>;<posicao>
def configurar_jogador(arquivo: str) -> list:
    posicoes = {}
    torpedo_posicoes = []
    for line in arquivo:
        codigo_str = line[0]
        if codigo_str in Configs.BOATS_ID.value:
            pos = line.strip().split(';')[1].split('|')
            posicoes.update({codigo_str: {}})
            for idx, peca in enumerate(pos):
                posicoes[codigo_str].update({idx: []})
                posicoes[codigo_str][idx].append(peca)
        elif codigo_str in Configs.TORPEDO_ID.value:
            pos = line.split(';')[1].split('|')
            for torpedo in pos:
                torpedo_posicoes.append(torpedo)

    for i,key in enumerate(posicoes.values()):
        if i+1 not in (3, '3'):
            for j,b in enumerate(key.values()):
                boat = boats[str(i+1)]
                for k in range(boat['max_posicoes']):
                    # TODO: BYPASS 'K' LETTER
                    p = (f'{chr(ord(b[0][0])+k)}{b[0][1:-1]}' if b[0][-1] == 'V' else f'{b[0][0]}{int(b[0][1:-1])+k}') if b[0][-1] in ('V', 'H') else (b)
                    b.append(p)
                b.pop(0)

    return posicoes, torpedo_posicoes

# STEP4 - VALIDAR QTT PECAS
def validar_qtt_pecas(posicoes: dict, torpedo: list) -> bool:
    return (
        len(torpedo) == 25 and len(posicoes) == 4 and len(posicoes['1']) == 5
        and len(posicoes['2']) == 2 and len(posicoes['3']) == 10 and len(posicoes['4']) == 5
        and all(len(value) == 4 for value in posicoes['1'].values())
        and all(len(value) == 5 for value in posicoes['2'].values())
        and all(len(value) == 1 for value in posicoes['3'].values())
        and all(len(value) == 2 for value in posicoes['4'].values())
    )

# STEP5 - VALIDAR SOBREPOSICAO DE PECAS
def validar_peca_ovw(posicoes: dict) -> bool:
    pecas = []
    result = {}
    for key in posicoes:
        for value in posicoes[key].values():
            for peca in value:
                pecas.append(peca)

    for peca in pecas:
        result.update({peca: pecas.count(peca)})

    return any(count == 1 for count in result.values())

# STEP6 - VALIDAR POSIÇÃO DAS PECAS
def validar_peca_pos(posicoes: dict, torpedos: list) -> bool:
    result = True
    for key in posicoes:
        for value in posicoes[key].values():
            for peca in value:
                if peca[0] not in Configs.VALID_COLUMNS.value:
                    result = False
                if int(peca[1:]) > 15:
                    result = False
    for torp in torpedos:
        if torp[0] not in Configs.VALID_COLUMNS.value:
            result = False
        if int(torp[1:]) > 15:
            result = False

    return result

# STEP7 - VALIDAR PONTOS
def calcular_pontuacao(posicoes: dict, torpedos: list) -> tuple:
    acertos: int = 0
    erros: int = 0
    for torp in torpedos:
        acerto: bool = False
        for enc in posicoes['1'].values():
            if torp in enc and acerto is False:
                acertos += 1
                enc.pop(enc.index(torp))
                acerto = True
        for poravi in posicoes['2'].values():
            if torp in poravi and acerto is False:
                acertos += 1
                acerto = True
                poravi.pop(poravi.index(torp))
        for sub in posicoes['3'].values():
            if torp in sub and acerto is False:
                acertos += 1
                acerto = True
                sub.pop(sub.index(torp))
        for cru in posicoes['4'].values():
            if torp in cru and acerto is False:
                acertos += 1
                acerto = True
                cru.pop(cru.index(torp))

        if acerto is False:
            erros += 1

    pont: int = 0
    for i, pos in enumerate(posicoes.values()):
        for j, boat in enumerate(pos.values()):
            if len(boat) < boats[f'{i+1}']['max_posicoes']:
                pont += ((boats[f'{i+1}']['max_posicoes'] - len(boat)) * 3) if len(boat) > 0 else 5

    return pont, acertos, erros

# STEP8 - GERAR SAIDA DE RESULTADO
def gerar_saida(pontuacao_j1: tuple, pontuacao_j2: tuple) -> None:
    resultado = {}
    file = open("resultado.txt", 'w')
    if pontuacao_j1[0] > pontuacao_j2[0]:
        resultado['jogador'] = 'J1'
        resultado['acertos'] = f'{pontuacao_j1[1]}AA'
        resultado['erros'] = f'{pontuacao_j1[2]}AE'
        resultado['pontuacao'] = f'{pontuacao_j1[0]}PT'
        file.write('J1 ' + f'{pontuacao_j1[1]}AA ' + f'{pontuacao_j1[2]}AE ' + f'{pontuacao_j1[0]}PT')
    elif pontuacao_j1[0] < pontuacao_j2[0]:
        resultado['jogador'] = 'J2'
        resultado['acertos'] = f'{pontuacao_j2[1]}AA'
        resultado['erros'] = f'{pontuacao_j2[2]}AE'
        resultado['pontuacao'] = f'{pontuacao_j2[0]}PT'
        file.write('J2 ' + f'{pontuacao_j2[1]}AA ' + f'{pontuacao_j2[2]}AE ' + f'{pontuacao_j2[0]}PT')
    else:
        file.write('J1 ' + f'{pontuacao_j1[1]}AA ' + f'{pontuacao_j1[2]}AE ' + f'{pontuacao_j1[0]}PT\n')
        file.write('J2 ' + f'{pontuacao_j2[1]}AA ' + f'{pontuacao_j2[2]}AE ' + f'{pontuacao_j2[0]}PT')



if __name__ == '__main__':
    resultado          = {}
    error_p1           = 0
    error_p2           = 0
    file               = receber_arquivo('jogador1.txt')
    p1_pos, p1_torpedo = configurar_jogador(file)
    qtt_pecas_validas_p1  = validar_qtt_pecas(p1_pos, p1_torpedo)
    ovw_pecas_validas_p1  = validar_peca_ovw(p1_pos)
    pos_pecas_validas_p1  = validar_peca_pos(p1_pos, p1_torpedo)
    pontuacao_p1          = calcular_pontuacao(p1_pos, p1_torpedo)
    if qtt_pecas_validas_p1 is False and error_p1 == 0:
        resultado['Jogador'] = 'J1'
        resultado['erro'] = Error.NR_PART.value
        error_p1 = 1
        with open("resultado.txt", 'w') as f:
            f.write(resultado['Jogador'] + " " + resultado['erro'])
    elif ovw_pecas_validas_p1 is False and error_p1 == 0:
        resultado['Jogador'] = 'J1'
        resultado['erro'] = Error.OVW_PIECE.value
        error_p1 = 1
        with open("resultado.txt", 'w') as f:
            f.write(resultado['Jogador'] + " " + resultado['erro'])
    elif pos_pecas_validas_p1 is False and error_p1 == 0:
        resultado['Jogador'] = 'J1'
        resultado['erro'] = Error.POS_NOEXIST.value
        error_p1 = 1
        with open("resultado.txt", 'w') as f:
            f.write(resultado['Jogador'] + " " + resultado['erro'])

    file               = receber_arquivo('jogador2.txt')
    p2_pos, p2_torpedo = configurar_jogador(file)
    qtt_pecas_validas_p2  = validar_qtt_pecas(p2_pos, p2_torpedo)
    ovw_pecas_validas_p2  = validar_peca_ovw(p2_pos)
    pos_pecas_validas_p2  = validar_peca_pos(p2_pos, p2_torpedo)
    pontuacao_p2          = calcular_pontuacao(p2_pos, p2_torpedo)
    if qtt_pecas_validas_p2 is False and error_p2== 0:
        resultado['Jogador'] = 'J2'
        resultado['erro'] = Error.NR_PART.value
        error_p2= 1
        with open("resultado.txt", 'w') as f:
            f.write(resultado['Jogador'] + " " + resultado['erro'])
    elif ovw_pecas_validas_p2 is False and error_p2== 0:
        resultado['Jogador'] = 'J2'
        resultado['erro'] = Error.OVW_PIECE.value
        error_p2= 1
        with open("resultado.txt", 'w') as f:
            f.write(resultado['Jogador'] + " " + resultado['erro'])
    elif pos_pecas_validas_p2 is False and error_p2== 0:
        resultado['Jogador'] = 'J2'
        resultado['erro'] = Error.POS_NOEXIST.value
        error_p2= 1
        with open("resultado.txt", 'w') as f:
            f.write(resultado['Jogador'] + " " + resultado['erro'])

    if error_p1 == 0 and error_p2 == 0:
        gerar_saida(pontuacao_j1=pontuacao_p1, pontuacao_j2=pontuacao_p2)