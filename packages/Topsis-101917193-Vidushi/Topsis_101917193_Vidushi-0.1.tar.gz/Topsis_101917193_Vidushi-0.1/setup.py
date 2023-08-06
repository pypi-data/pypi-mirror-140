from distutils.core import setup
setup(
  name = 'Topsis_101917193_Vidushi',         # How you named your package folder (MyLib)
  packages = ['Topsis_101917193_Vidushi'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  #description = 'TYPE YOUR DESCRIPTION HERE',   # Give a short description about your library
  author = 'Vidushi Goyal',                   # Type in your name
  author_email = 'goyalvidushi2@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/vidushi2001',   # Provide either the link to your github or to your website
  download_url = "https://github.com/vidushi2001/Topsis/archive/refs/tags/0.1.tar.gz",# I explain this later on
  keywords=['topsis', 'Rank', 'Best', 'Model'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'pandas',
      ],
  classifiers=[
        "Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
  ],
)