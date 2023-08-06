from setuptools import setup  
requirements = ["Pygame==2.1.1","keyboard","pygame_widgets","colorama"]
setup(name='pygl_np',
       version='15.5.122c3',
       description='small and compact graphick distributions',
       packages=['pygl'],       
       author_email='pvana621@gmail.com', 
       install_requires=requirements,      
       zip_safe=False)