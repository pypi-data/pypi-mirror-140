"""
Aqui estão alguns arquivos que foram pensados mas não usados. Assim, não foram
testados e muito menos atualizados ao longo das mudanças feitas na biblioteca.
Foram deixados aqui porque se no futuro essas funções vierem a calhar, o código
já escrito pode dar ideias e acelerar a implementação.
"""


def set_additional_info(spectrum, info):
    """
    Adiciona informações adicionais ao espectro, como medidas, por exemplo
    O problema por enquanto é que adiciona o mesmo dicionário em todos, o que
    não é muito útil

    :param info: Um dicionário com as informações a serem adicionadas.
        Ex: { 'periodo': 400 , 'temp': 20, 'strain': 200, 'mode': 4 }
    :type info: dict

    :return: None
    """
    return spectrum, info


def fbg_modulation(natural_wl, shifts):
    """
    TODO checar, peguei de um lugar antigo e não lembro onde foi usado

    Simula a mudança do comprimento de onda ressonante da FBG com a mudança
    de temperatura e/ou deformação. Em geral, as sensibilidades ficam em torno
    de (Esses valores são usados nas sensibilidades geradas automaticamente):
        - dwl/dstrain ~= 1pm/mue
        - dwl/dTemp   ~= 10pm/°C

    :param natural_wl: Os comprimentos de onda ressonantes nos valores de
        referência de deformação e temperatura (shift=0).
    :type natural_wl: array like

    :param shifts: Um dicionário contendo as mudanças de temperatura e
        deformação. (Como {'strain': 200, 'temp': 5}).
    :type shifts: dict

    :return: Os comprimentos de onda calculados após as mudanças. Tem o mesmo
        tamanho do array de natural_wl.

    """

    raise NotImplementedError()

    sensibilities = dict()
    keys = shifts.keys()
    found_any = False

    if 'strain' in keys:
        sensibilities['strain'] = \
            1e-12 + 1e-13 * np.random.standard_normal(len(natural_wl))
        found_any = True

    if 'temp' in keys or 'temperature' in keys:
        sensibilities['temp'] = \
            10*(1e-12 + 1e-13*np.random.standard_normal(len(natural_wl)))
        found_any = True

    if not found_any:
        raise Exception('Invalid shifts. Shifts should be a dictionary with '
                        '"temp" or "strain" in its keys and the values for '
                        'those shifts as values.')

    wl = []
    for i in range(0, len(natural_wl)):
        new_wl = natural_wl[i]
        for s in sensibilities.keys():
            new_wl += sensibilities[s][i]*shifts[s][i]
        wl.append(new_wl)

    return np.asarray(wl)


def simulate_optical_noise(spectrum, noise, unit='dB'):
    """
    TODO checar, pq acho q o ruído n seria multiplicado, testar tb
    Adiciona ruído optico no espectro

    :param spectrum: O objeto de espectro em que o ruído será introduzido. A
        mudança é realizada inplace.
    :type spectrum: SpectrumData

    :param noise: O ruído a ser adicionado. Se for float, será usado como
        variância na geração de um np array aleatório com distribuição normal
    :type noise: float ou np array

    :param unit: A unidade do espectro. dB por padrão
    :type unit: string
    """

    raise NotImplementedError()

    # Gera o noise se ele for escalar
    if type(noise) == float or type(noise) == int:
        noise = np.random.randn(spectrum.shape[0]) * noise

    if unit == 'dB':
        spectrum[::, 1] += noise
    elif unit == 'scalar':
        spectrum[::, 1] *= noise
    else:
        raise ValueError('Unidade inválida. As implementadas são "dB" e '
                         '"scalar"')

