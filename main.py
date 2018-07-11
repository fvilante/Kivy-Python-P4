# Aqui le-se todos os arquivos necessarios ao funcionamento do sistema.

import toml
from enum import Enum, unique, auto
from random import randint

ConfigFile = {
    "Matriz" : '.\config\matrizes.toml',
    "Config" : '.\config\configuracao.toml',
    "CMPP00LG": '.\config\CMPP00LG.toml',
    "POS_Padrao": r'.\config\pos_padrao.toml',
}


def _readConfigFile(FileType):
    with open(ConfigFile[FileType], 'r') as myfile:
        dict_ = toml.load(myfile)
    return dict_

def getMatriz(barcode):
    dict_ = _readConfigFile('Matriz')
    return dict_['matriz'][barcode]

def _getCabecote(cor):
    dict_ = _readConfigFile('Config')
    return dict_['cabecote'][cor]

def getCabecoteBranco(): return _getCabecote('branco')
def getCabecotePreto(): return _getCabecote('preto')


def _getEixo(eixo):
    dict_ = _readConfigFile('Config')
    return dict_['eixo'][eixo]

def getEixoX(): return _getEixo('x')
def getEixoY(): return _getEixo('y')
def getEixoZ(): return _getEixo('z')

def _getMemMap(param):
    dict_ = _readConfigFile('CMPP00LG')
    #todo: validate memmap
    return dict_[param.name]

class Enum_AutoName(Enum):
     def _generate_next_value_(name, start, count, last_values):
         return name


class Param(Enum_AutoName):
    # arquivo de eixo(apenas referente a placa CMPP)
    Posicao_inicial = auto()
    Posicao_final = auto()
    Aceleracao_de_avanco = auto()
    Aceleracao_de_retorno = auto()
    Velocidade_de_avanco = auto()
    Velocidade_de_retorno = auto()
    Numero_de_mensagens_no_avanco = auto()
    Numero_de_mensagens_no_retorno = auto()
    Posicao_da_primeira_impressao_no_avanco = auto()
    Posicao_da_primeira_impressao_no_retorno = auto()
    Posicao_da_ultima_impressao_no_avanco = auto()
    Posicao_da_ultima_impressao_no_retorno = auto()
    Largura_do_sinal_de_impressao = auto()
    Tempo_para_start_automatico = auto()
    Tempo_para_start_externo = auto()
    Antecipacao_da_saida_de_start = auto()
    # configuracao de eixo(apenas referente a placa CMPP)
    Janela_de_protecao_para_o_giro = auto()
    Numero_de_pulsos_por_giro_do_motor = auto()
    Valor_da_posicao_de_referencia = auto()
    Aceleracao_de_referencia = auto()
    Velocidade_de_referencia = auto()
    # CMDFLASH = 96(0x60)
    Start_automatico_no_avanco = auto()
    Start_automatico_no_retorno = auto()
    Saida_de_start_no_avanco = auto()
    Saida_de_start_no_retorno = auto()
    Entrada_de_start_externo = auto()
    Logica_de_start_externo = auto()
    Entrada_de_start_entre_eixos = auto()
    Referencia_pelo_start_externo = auto()
    Logica_de_sinal_de_impressao = auto()
    Logica_de_sinal_de_reversao = auto()
    Selecao_de_mensagem_via_serial = auto()
    Reversao_de_mensagem_via_serial = auto()
    Giro_com_funcao_de_protecao = auto()
    Giro_com_funcao_de_correcao = auto()
    Reducao_da_corrente_de_repouso = auto()
    Modo_continuo_passo_a_passo = auto()

    
    
    
    
    


def getArquivoPos(nome):
    dict_ = _readConfigFile('POS_Padrao')
    return dict_['POS'][nome]

def _dictOverride(base, overrider):
    dict_ = base
    dict_.update(overrider)
    dict_.pop('Inhirit', None)
    return dict_



def convertInt(value):
    if value > 255: value = 255  # todo: log error
    dado = (value).to_bytes(2, byteorder='little', signed=False)
    dadoL = dado[0]
    dadoH = dado[1]
    return dadoL, dadoH

ESC = 27
STX = 2
ETX = 3
ACK = 6
NACK = 21

DIRECAO_SOLICITACAO = (0<<6) + (0<<7)
DIRECAO_MASCARA_RESETAR_BITS = (0<<6) + (1<<7)
DIRECAO_MASCARA_SETAR_BITS = (1<<6) + (0<<7)
DIRECAO_ENVIO = (1<<6) + (1<<7)

NO_ERROR = 0
HAS_ERROR = 1


def duplicaSeEsc(value:int): #-> List[int] or List{int, int]:
    r_ = [value]
    if value == ESC:
        r_.append(ESC)
    return r_

def calculaChecksum(direcao, canal, comando, dadoL, dadoH): #->Int
    mylist = [
        int(STX),
        int(direcao),
        int(canal),
        int(comando),
        int(dadoL),
        int(dadoH),
        int(ETX),
    ]
    checksum = 0
    for each in mylist:
        checksum = checksum + each
        while checksum > 256:
            checksum = checksum - 256

    checksum = 256 - checksum
    return checksum


def enviaPacote(direcao, canal, memmap, dadoH, dadoL ):

    comando = int(memmap['comando'])
    direcao_e_canal = int(direcao+canal)

    checksum = calculaChecksum(direcao, canal, comando,
                               dadoL, dadoH)
    pacote = [
        [ESC,STX],
        duplicaSeEsc(direcao_e_canal),
        duplicaSeEsc(comando),
        duplicaSeEsc(dadoH),
        duplicaSeEsc(dadoL),
        [ESC,ETX],
        duplicaSeEsc(checksum),
    ]

    pacote_list = [item for sublist in pacote for item in sublist]
    pacote_bytes = bytes(pacote_list)
    pacote_bytes_hex = [hex(each) for each in list(pacote_bytes)]

    print("Enviando bytes:")
    print(memmap['descricao'])
    print(list(pacote_bytes_hex))

    return NO_ERROR


def sendWordToCMPP(canal, memmap, value):
    dadoL, dadoH = convertInt(value)
    direcao = DIRECAO_ENVIO
    err_ = enviaPacote(direcao, canal, memmap, dadoL, dadoH)
    return err_

def sendBitToCMPP(canal, memmap, value):
    if (value >= 2): value=0 #todo: log error: type mismach
    if value == 0:
        direcao = DIRECAO_MASCARA_RESETAR_BITS
    else:
        direcao = DIRECAO_MASCARA_SETAR_BITS
    value = value << int(memmap['startbit'])
    dadoL, dadoH = convertInt(value)
    err_ = enviaPacote(direcao, canal, memmap, dadoL, dadoH)
    return err_

def sendByteToCMPP(canal, memmap, value):
    err_ = NO_ERROR
    return err_


def sendParamToCMPP(canal, memmap, value):
    if canal > 64: canal=64 #todo: log error 'channel overflow'
    if (type(value) is int):
        if value > 65535: value=0 #todo: log error 'value overflow'
    bitlen = memmap['bitlen']

    if (bitlen == 16):
        err = sendWordToCMPP(canal, memmap, value)
    elif (bitlen == 1):
        err = sendBitToCMPP(canal, memmap, value)
    elif (bitlen == 8):
        print("Estrategia: Byte - Nao implementado")
        err = sendByteToCMPP(canal, memmap, value)
    else:
        #todo: log error 'bitlen has no strategy, skiped!'
        DoNothing = 0


def sendPOStoCMPP(canal, POS ):
    for key, value in POS.items():
        memmap = _getMemMap(Param(key))
        value = randint(0,255)
        err_ = sendParamToCMPP(canal, memmap, value)
        if err_ == HAS_ERROR:
            print("ERRO") #todo: log error


if __name__ == "__main__":

    barcode = '10101010'
    print(getMatriz(barcode))
    print(getCabecoteBranco())
    print(getCabecotePreto())
    print(getEixoX())
    print("\n")
    print(_getMemMap(Param.Aceleracao_de_avanco))
    print(getArquivoPos('base'))
    print(getArquivoPos('referenciar_z'))
    print(getArquivoPos('referenciar_z')[Param.Aceleracao_de_avanco.value])
    base = getArquivoPos('base')
    overrider = getArquivoPos('referenciar_x')
    print("\n")
    print(base)
    print(overrider)
    print(_dictOverride(base, overrider))

    arquivoPOS = getArquivoPos('base')
    print("\n TESTA PROTOCOLO SERIAL:")
    print(arquivoPOS)
    sendPOStoCMPP(3, arquivoPOS)

    print("\n")
    memmap = {
        'comando': 0x83,
        'descricao': "TESTE ---- ******* AHAH*****"
    }
    enviaPacote(DIRECAO_SOLICITACAO, 1,
                memmap, 0x36, 0x37)





