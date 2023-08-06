from distutils.core import setup
setup(
  name = 'graphics_pack',         # How you named your package folder (MyLib)
  packages = ['graphics_pack'],   # Chose the same as "name"
  version = '0.1',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Graphics library for some uses in exploratory analysis',   # Give a short description about your library
  author = 'Yaniela',                   # Type in your name
  author_email = 'yanielajanis@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/yaniela/publish_my_own_package',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/yaniela/publish_my_own_package/archive/refs/tags/v1.0.tar.gz',    # I explain this later on
  keywords = ['graphics', 'colors', 'palette'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'seaborn',
          'matplotlib.pyplot',
          'datetime',
          'numpy',
          'july',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.9',
  ],
)

