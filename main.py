# Aqui le-se todos os arquivos necessarios ao funcionamento do sistema.

import toml
from enum import Enum, IntEnum, auto
from random import randint
from time import sleep


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

class Err(IntEnum):
    SUCESSFUL = 0
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


def criaPacote(direcao, canal, memmap, dadoH, dadoL): #-> list
    comando = int(memmap['comando'])
    direcao_e_canal = int(direcao + canal)

    checksum = calculaChecksum(direcao, canal, comando,
                               dadoL, dadoH)
    pacote = [
        [ESC, STX],
        duplicaSeEsc(direcao_e_canal),
        duplicaSeEsc(comando),
        duplicaSeEsc(dadoL),
        duplicaSeEsc(dadoH),
        [ESC, ETX],
        duplicaSeEsc(checksum),
    ]

    pacote_list = [item for sublist in pacote for item in sublist]
    return pacote_list  #-> list, err

def interpretaPacoteEnviado(parsed_pack):
    direcao:int = parsed_pack[State.DIRECTION]
    result = dict()
    if direcao == DIRECAO_SOLICITACAO:
        result['Tipo'] = 'Pacote de solicitacao'
    elif direcao == DIRECAO_ENVIO:
        result['Tipo'] = 'Pacote de envio'
    elif direcao == DIRECAO_MASCARA_SETAR_BITS:
        result['Tipo'] = 'Mascara para setar bits'
    elif direcao == DIRECAO_MASCARA_RESETAR_BITS:
        result['Tipo'] = 'Mascara para resetar bits'
    else:
        result['Tipo'] = 'Indefinido'


    return result

def interpretaPacoteRecebido(pacote_recebido, pacote_enviado):
    info = dict()
    start_byte = pacote_recebido[State.START_BYTE]

    #Start Byte
    if start_byte == ACK :
        info['Tipo'] = "Retorno sem erro"
    elif start_byte == NACK:
        info['Tipo'] = "Retorno com erro"
    else:
        info['Tipo'] = 'Indefinido?1?' #@@@

    #Status
    tipo_de_envio = pacote_enviado[State.DIRECTION]
    tipo_de_retorno = pacote_recebido[State.START_BYTE]
    dadoL = pacote_recebido[State.DATA_LOW]
    dadoH = pacote_recebido[State.DATA_HIGH]
    info['StatusL'] = None
    info['StatusH'] = None
    info['Byte_de_Erro'] = None
    info['Dado'] = None
    if tipo_de_retorno == ACK:
        if tipo_de_envio == DIRECAO_SOLICITACAO:
            info['Dado'] = ((int(dadoH))*256) + (int(dadoL))
        else:
            info['StatusL'] = dadoL
            info['StatusH'] = dadoH
    elif tipo_de_retorno == NACK:
        info['StatusL'] = dadoL
        info['Byte_de_Erro'] = dadoH

    return info

RawPacket = 'RawPacket'
Parsed = 'Parsed'
Summary = 'Summary'
Transmission = 'Transmission'
Reception = 'Reception'


def transceiveCmpp(porta, direcao, canal, param, dadoL, dadoH):

    memmap = _getMemMap(param)
    transaction_report = dict()
    transmission = dict()
    reception = dict()

    #todo: improve piping infra-structure

    pacote_envio_raw :bytes = criaPacote(
                        direcao, canal, memmap, dadoL, dadoH )
    #todo: document 'transaction data structure'
    pacote_enviado_parsed = parsePacote(pacote_envio_raw)
    #todo: if parsing has error don't send packet, handle error
    summary_info = interpretaPacoteEnviado(pacote_enviado_parsed)

    transmission[RawPacket] = pacote_envio_raw
    transmission[Parsed] = pacote_enviado_parsed
    transmission[Summary] = summary_info

    transaction_report[Transmission] = transmission

    #data-link
    pacote_recebido_raw :bytes = transmiteSerial(porta, pacote_envio_raw)
    pacote_recebido_parsed = parsePacote(pacote_recebido_raw)
    resposta_interpretada = \
        interpretaPacoteRecebido(
            pacote_recebido_parsed,
            pacote_enviado_parsed)

    reception[RawPacket] = list(pacote_recebido_raw)
    reception[Parsed] = pacote_recebido_parsed
    reception[Summary] = resposta_interpretada

    transaction_report[Reception] = reception

    print('Transacao:')
    print(transaction_report, "\n")


    return transaction_report


def transmiteSerial(porta, pacote_list):
    #envia
    for each in pacote_list:
        byte = bytes([each])
        sendByteThroughSerial(porta, byte)

    #aguarda retorno
    #sleep(0.5)

    #recebe
    bytes_recebidos : bytes = readBytesFromSerial(porta)
    return bytes_recebidos

class State(Enum_AutoName):
    INITIAL_ESC = auto() #1
    START_BYTE = auto() #2
    DIRECTION = auto() #3.0
    CHANNEL = auto() #3.1
    COMMAND = auto() #4
    DATA_LOW = auto() #5
    DATA_HIGH = auto() #6
    FINAL_ESC = auto() #7
    ETX_BYTE = auto() #8
    CHECKSUM = auto() #9
    SUCESSFUL = auto() #10

def parsePacote(pacote : bytes): #-> dict, int
    pacote = list(pacote)

    state = State.INITIAL_ESC
    checkSum = 0
    duplicateESC = False
    result = dict()
    result_parsed = dict()

    for byte in pacote:

        if ((duplicateESC == True) and (byte == ESC)):
            duplicateESC = False
            continue

        #ESC-duplication code
        if ( (byte == ESC)
                and ((state != State.INITIAL_ESC)
                     and state != (State.FINAL_ESC)) ):
            duplicateESC = True

        #Calculate checksum
        if (( (state != State.INITIAL_ESC)
              and (state != State.FINAL_ESC))
                and (state != State.CHECKSUM)):
            checkSum = checkSum + byte
            while checkSum > 256:
                checkSum = checkSum - 256

        #explode bytes of packet in a dictionary
        if state == State.INITIAL_ESC:
            if (byte == ESC):
                result_parsed[state] = byte
                state = State.START_BYTE
            continue
        elif state == State.START_BYTE:
            if (byte == STX) \
                    or (byte == ACK) \
                    or (byte == NACK) :
                result_parsed[state] = byte
                state = State.DIRECTION
            continue
        elif state == State.DIRECTION: #or state == State.CHANNEL:
            direction = (byte >> 6) << 6
            result_parsed[State.DIRECTION] = direction
            state == State.DIRECTION
            result_parsed[State.CHANNEL] = byte - direction
            state = State.COMMAND
            continue
        elif state == State.COMMAND:
            result_parsed[state] = byte
            state = State.DATA_LOW
            continue
        elif state == State.DATA_LOW:
            result_parsed[state] = byte
            state = State.DATA_HIGH
            continue
        elif state == State.DATA_HIGH:
            result_parsed[state] = byte
            state = State.FINAL_ESC
            continue
        elif state == State.FINAL_ESC:
            if (byte == ESC):
                result_parsed[state] = byte
                state = State.ETX_BYTE
            continue
        elif state == State.ETX_BYTE:
            if (byte == ETX):
                result_parsed[state] = byte
                state = State.CHECKSUM
            continue
        elif state == State.CHECKSUM:
            checkSum = 256 - checkSum
            result_parsed[state] = byte
            if (checkSum == byte):
                state = State.SUCESSFUL
            continue
        elif state == State.SUCESSFUL:
            result_parsed[state] = True
            #??
            continue
        else:
            continue

    if state == State.SUCESSFUL:
        result_parsed['Err'] = Err.SUCESSFUL
    else:
        result_parsed['Err'] = Err.HAS_ERROR
        #todo: return more details of error


    return result_parsed #dict, int


#put one byte on serial port
def sendByteThroughSerial(porta, byte : bytes):
    return

#read the entire reception buffer of serial port
def readBytesFromSerial(porta):
    resposta = [
        ESC,
        ACK,
        0xC1,
        0x52,
        0x00,
        0x00,
        ESC,
        ETX,
        0xE4,
    ]
    return bytes(resposta)

def sendWordToCMPP(porta, canal, param, value):
    dadoL, dadoH = convertInt(value)
    direcao = DIRECAO_ENVIO
    result = transceiveCmpp(porta, direcao, canal, param, dadoL, dadoH)
    return result

def sendBitToCMPP(porta, canal, param, value):
    if (value >= 2): value=0 #todo: log error: type mismatch
    if value == 0:
        direcao = DIRECAO_MASCARA_RESETAR_BITS
    else:
        direcao = DIRECAO_MASCARA_SETAR_BITS
    value = value << int(_getMemMap(param)['startbit'])
    dadoL, dadoH = convertInt(value)
    result = transceiveCmpp(porta, direcao, canal, param, dadoL, dadoH)
    return result

def sendByteToCMPP(porta, canal, param, value):
    if (value >= 256): value = 0  # todo: log error: type mismatch
    startbit = _getMemMap(param)['startbit']
    comando = _getMemMap(param)['comando']
    bitlen = _getMemMap(param)['bitlen']
    dadoL = int(0)
    dadoH = int(0)
    result = dict()

    #invariant
    if (startbit !=8 or startbit != 0): pass # todo:logo error: padding mismatch

    # Get current word from CMPP
    result = transceiveCmpp(porta, DIRECAO_SOLICITACAO, canal, param, dadoL, dadoH)
    if result[Transmission][Summary]['Tipo'] == 'Retorno com erro':
        pass #todo handle exception
    dadoL = result[Transmission][Parsed][State.DATA_LOW]
    dadoH = result[Transmission][Parsed][State.DATA_HIGH]

    # Overwrite byte I want to send
    if (startbit == 8): dadoH = value
    if (startbit == 0): dadoL = value

    # Send new information to CMPP
    result = transceiveCmpp(porta, DIRECAO_ENVIO, canal, param, dadoL, dadoH)
    return result


def sendParamToCMPP(porta, canal, param, value):
    if canal > 64: canal=64 #todo: log error 'channel overflow'
    if (type(value) is int):
        if value > 65535: value=0 #todo: log error 'value overflow'
    bitlen = _getMemMap(param)['bitlen']

    if (bitlen == 16):
        result = sendWordToCMPP(porta, canal, param, value)
    elif (bitlen == 1):
        result = sendBitToCMPP(porta, canal, param, value)
    elif (bitlen == 8):
        print("Estrategia: Byte - Nao implementado")
        result = sendByteToCMPP(porta, canal, param, value)
    else:
        #todo: log error 'bitlen has no strategy, skiped!'
        DoNothing = 0

    return result


def sendPOStoCMPP(porta, canal, POS ):

    # envia parametro por parametro do POS especificado
    for key, value in POS.items():
        param = Param(key)
        #todo: handle, it may trow or do something else if key doesn't match
        value = randint(0,255)
        result = sendParamToCMPP(porta, canal, param, value)
        if result[Transmission][Summary] == 'Retorno com erro':
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
    porta = 'COM1'
    sendPOStoCMPP(porta, 3, arquivoPOS)



    print("Teste:")
    memmap = _getMemMap(Param.Aceleracao_de_avanco)
    retorno = criaPacote(DIRECAO_SOLICITACAO, 1,
                memmap, 0x36, 0x37)
    print(retorno)
    retorno_parsed = parsePacote(retorno)
    print(retorno_parsed)

    print("\n")
    retorno = readBytesFromSerial(list())
    parsePacote(retorno)



    print("\n")
    memmap = {
        'comando': 0x83,
        'descricao': "TESTE ---- ******* AHAH*****"
    }
    transceiveCmpp(porta, DIRECAO_SOLICITACAO, 1,
                   Param.Aceleracao_de_avanco, 0x36, 0x37)




