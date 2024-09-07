def process_word(word):
    codigo_barra = [0] * 12

    if len(word) == 2:
        codigo_barra[5] = int(word[0])
        codigo_barra[11] = int(word[1])
    
    elif len(word) == 5:
        codigo_barra[5] = int(word[0])
        codigo_barra[6:8] = [0] * 2
        codigo_barra[8:] = [int(c) for c in word[1:]]
        
    elif len(word) == 6:
        codigo_barra[5] = int(word[0])
        codigo_barra[6] = 0 
        codigo_barra[7:] = [int(c) for c in word[1:]]
    
    elif len(word) >= 7:
        metragem = word[-6:]  
        id_part = word[:-6]
        
        for i in range(min(6, len(id_part))):
            codigo_barra[i] = int(id_part[i])
        
        for i in range(len(metragem)):
            codigo_barra[6 + i] = int(metragem[i])
    
    id_str = ''.join(str(c) for c in codigo_barra[0:6])
    metragem_str = ''.join(str(c) for c in codigo_barra[6:12])
    
    return id_str, metragem_str

# Testes
word = input()

id1, metragem1 = process_word(word)

print(id1, metragem1)
