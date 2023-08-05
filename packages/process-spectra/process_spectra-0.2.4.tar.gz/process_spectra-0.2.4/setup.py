# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['process_spectra', 'process_spectra.funcs', 'process_spectra.utils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.3.2,<4.0.0',
 'numpy>=1.20.0,<2.0.0',
 'pandas>=1.3.4,<2.0.0',
 'scipy>=1.6.2,<2.0.0']

setup_kwargs = {
    'name': 'process-spectra',
    'version': '0.2.4',
    'description': 'A package designed to process optical spectra of fiber optic sensors based on long period gratings (LPGs).',
    'long_description': "# process_spectra\n\nThis is the repo for the process_spectra package. It is a package designed to process optical spectra of fiber optic sensors based on long period gratings (LPGs). The documentation is written in portuguese, since the project was conceived to improve research at a brazilian university lab (LITel - UFJF). If the contents of the library may be useful to you, and you do not speak portuguese, please send us an e-mail or open an issue.\n\nPacote python feito com o intuito de processar o espectro óptico de sensores ópticos a fibra baseados em grades de periodo longo (LPGs). Com esse pacote é possível fazer a extração de dados de conjuntos grandes de espectros, seguindo uma rotina específica. \n\n## Instalação:\n\nO pacote foi colocado no PyPi, logo é possível instalar pelo pip:\n\n```\npip install process_spectra\n```\n\n## Como usar:\n\nPara usar o pacote, basta criar um objeto da classe *MassSpectraData*, adicionar passos com os devidos argumentos e rodar. Como um exemplo simples que extrai os vales ressonantes de espectros na pasta *spectra*:\n\n``` python\nimport os\nimport process_spectra as ps\n\n\n# Criando a lista de caminhos\nfiles = os.listdir('spectra')\nfiles_complete = [os.path.join('spectra', x) for x in files]\n\n# Criando o objeto, passando a lista e o nome do arquivo para \n# salvar as informações extraídas\nspectra = ps.MassSpectraData(files_complete, 'resonant_wavelengths.csv')\n\n\n# Adicionando o passo de extração, com um dicionário de argumentos \n# para a função do passo\nspectra.add_step(ps.funcs.find_valley, {'prominence': 5, 'ignore_errors': True})\n\nspectra.run(ignore_errors=True)\n\n```\n\nVale notar que os ignore_errors são passados para evitar que o programa encerre no caso de encontrar algum. Isso é útil quando não se tem certeza da integridade de todos os espectros, visto que se um estiver corrompido, o programa pode travar nele.\n\nNa pasta de exemplos estão alguns scripts que foram escritos para e usados em pesquisas, e mostram mais funcionalidades do pacote.\n\n## Documentação\n\nA documentação não foi publicada em sites, mas foi colocada no código, então é possível encontrar ela através do comando help() do python, passando como argumento uma classe, função ou módulo, ou também lendo do código direto.\n\nTambém é possível gerar a documentação através do sphinx. Basta clonar / baixar o repositórrio, abrir um cmd na pasta sphinx e rodar o comando \n\n```\nmake html\n```\n\nA documentação será gerada em html, como um site, e pode ser encontrada no caminho *sphinx/_build/html/index.html*.",
    'author': 'Felipe Barino',
    'author_email': 'felipebarino@gmail.com',
    'maintainer': 'Guilherme Sampaio',
    'maintainer_email': 'guilherme_albuquerque2@hotmail.com',
    'url': 'https://github.com/felipebarino/process_spectra',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
