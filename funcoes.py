# funcoes
def formata_numero(valor, prefixo = ''):
    multi = [10**9, 10**6, 10**3]
    unidade = ['bilhões', 'milhões', 'mil']
    pos = 0
    for prm in multi:
        if valor >= prm:
            valor = valor / prm
            return f'{prefixo} {valor:.2f} {unidade[pos]}'
        pos += 1 
    return f'{prefixo} {valor:.2f}'