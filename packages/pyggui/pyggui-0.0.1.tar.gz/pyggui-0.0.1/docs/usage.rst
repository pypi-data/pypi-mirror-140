=====
Usage
=====

Setup
-----
Install the library from PyPI, prefferably into a virtual environment. Creating a virtual environment (venv) helps if your project will later be packaged with a tool like Pyinstaller.

Create your project directory::

    > mkdir MyNewProject
    
Create virtual environment inside the directory::

    > cd MyNewProject  # Move into directory
    > python -m venv venv  # Create venv (Path to venv will look like this: /path/to/MyNewProject/venv)
    
Activate virtual environment and install the library using Pip::

    > venv/scripts/activate  # Activate, a (venv) will appear at the beggining of the command line
    (venv)> pip install pyggui
    
To use pyggui in a project::

	import pyggui
    
As the project consists of multiple packages and modules it is recomended that each item, class or function is imported separatley. 

Project structure
-----------------

Recomended project structure is as follows::
    
    MyNewProject/
        venv/
        assets/  # All assets (images, sounds, etc.)
        pages/  # Page python files 
        logic/  # Custom logic such as a Player module, Entity, Map, etc.
        main.py
        __init__.py

Ofcourse you can personalize you structure as you want, but having a main file is recomended (again because of packaging).
Optionally the library has a client included for command line tools where the above described directory structure can be generated automatically, see paragraph below. 

Generate project structure
==========================
Generate you projects structure using one command. This will copy all needed directories and files into your project so you can get straight into coding!

Activate virtual environment and call Pythons make command passing it pyggui::
    
    (venv)> python -m pyggui
    
This will then create the above structure in the directory where the virtual environment is contained.
Optionally you can pass the -p parameter specifying where the structure should be created, in case you're not running from inside your virtual environment::

    > python -m pyggui -p=C:\absolute\path\to\project\directory\MyNewProject
    
Getting started
---------------
The library is oriented around pages, where pages are custom classes you create and add items to (such as buttons, images, ...). Pages are stored, and handled inside the controller object. Everything along with the main loop, controller, input and window is defined inside the Game object. 

Main file and Game object
=========================
Creating our main loop is done by initializing the Game object to which we can set some global properties and settings::

    from pyggui import Game
    
    game = Game(
        display_size = (720, 360),  # Define display size 
        page_directory = "pages"  # Optionally pas the directory where pages are defined, this helps internally as pages are automatically found and imported
        entry_page = "WelcomePage",  # Optionally set the entry page to your game, this will be more clear as we create some pages 
        fps = 60,  # Optionally set an FPS cap
        display = my_custom_surface  # Optionally pass your own custom pygame.surface.Surface object with your own settings
    )
    
    if __name__ == '__main__':
        game.run()  # Run the main loop

There are more parameters you can set but the above ones are the basics, none of them are needed for a basic loop. 
Try running the code below, this will open a default page::

    from pyggui import Game
    
    game = Game()
    
    if __name__ == '__main__':
        game.run()

Pages and Controller
====================
The whole project is based around pages and the controller object. Pages are custom classes that inherit from the :code:`pyggui.gui.Page` class. Once you create a custom page, it gets automatically detected and imported by the controller, it is also added to the controllers pages dictionary attribute. This simplifies importing and redirecting between pages. Each page recieves the controller object so you should always include it in the :code:`__init__` methods arguments.

Let's define a simple page. 
First create the pages py file inside pages (MyNewProject/pages/welcome_page.py)::

    from pyggui.gui import Page
    
    class WelcomePage(Page):
        def __init__(self, controller):  # Always have a parameter for controller
            super().__init__(controller)  # Initialize parent class and pass it the controller object
            
This is all that is needed for creating a simple page. 
If we want this to be our landing page in the game, we pass the classes name as a string in the Games class parameter entry_page::

    game = Game(
        page_directory="pages",  # Set directory where pages are defined
        entry_page="WelcomePage"
    )

Controller stores every defined page in our project in the pages attribute, where the key is the class name of page as a string.
More about this in the controllers documentation TODO add link to docs.

Redirecting between pages can be done using controllers redirect_to_page method, where you pass it the pages name as a parameter.
Lets define a send page and redirect to it as we land on the WelcomePage::


    from pyggui.gui import Page
    
    class SecondPage(Page):
        def __init__(self, controller):
            super().__init__(controller)
            
            print("We are on the SecondPage")
    
    
    class WelcomePage(Page):
        def __init__(self, controller):
            super().__init__(controller)
            
            print("We are on the WelcomePage")
            
            # Instantly redirect
            print("Redirecting...")
            self.controller.redirect_to_page("SecondPage")  # Notice the controller is an attribute, this gets set when we call supers __init__ method above,
                                                            # Controller can also be accesed without self (i.e. controller.redirect_to_page("SomePage")) inside the innit method.
            
The code defined above will give the following output once the game.run() method is ran::

    >>> We are on the WelcomePage
    >>> Redirecting...
    >>> We are on the SecondPage
    
Redirecting can ofcourse be used as an "on click" method with different items, more on that in the below paragraph once we learn to add different items. 
Pages can also have different parameters you can pass, but must always have the controller as the first parameter.

See the Page documentation TODO Add link
          
Adding and controlling Gui elements
===================================

The library consists of many gui elements (called items) you can use. Items can be personalized by passing custom images, sprites or folders containing images used for animations. However if you initially wish to only experiment (and later create your custom images), you can use default items. Default items are defined inside the library and behave exactly like your custom items but have some basic pre-defined animations and looks.

We add each item to a page, we do that inside the init method using the add_item method.

Lets add a simple text item to our WelcomePage::

    from pyggui.gui import Page, Text  # Text class for displaying text on screen

    class WelcomePage(Page):
        def __init__(self, controller):
            super().__init__(controller)
            
            self.add_item(
                item=Text(
                    position=[100, 100],  # Position on screen (and page) to add the item at (upper left corner of item)
                    value="Welcome!",  # Text value to display
                    font_size=40,  # Define the size of the font, 40 in this case as we want it to be big
                )
            )
            
You can store the item in a pages attribute so you can access it from different method, or other items::

    class WelcomePage(Page):
        def __init__(self, controller):
            super().__init__(controller)
            
            self.text = Text(  # Define the item, store in attribute
                position=[100, 100],  # Position on screen (and page) to add the item at (upper left corner of item)
                value="Welcome!",  # Text value to display
                font_size=40,  # Define the size of the font, 40 in this case as we want it to be big
            )
            # Add it later, do not forget this
            self.add_item(self.text)

Above will now have a bigger text (Welcome!) on screen with the libraries default font. Ofcourse we can also add our custom font to the text, more on that here: Text documentation. TODO add link.

Some items have to have the controller passed to them. Controller can view mouse position, clicks, etc. so it is used for detecting hovering above item or clicking on said item.

Lets add a simple button that redirects to our other SecondPage::

    from pyggui.gui import Button
    from pyggui.helpers import create_callable

    class WelcomePage(Page):
        def __init__(self, controller):
            super().__init__(controller)
            
            # Above defined text should be here
            
            self.redirect_to_second_page_button = Button(
                controller=self.controller,  # Pass it the controller object
                position=[100, 300],  # Set some position
                size=[120, 40],   # Set some size
                text="Go to second page",  # Give the button text as a string or pass your own Text item.
                on_click=create_callable(self.controller.redirect_to_page, "SecondPage")  # Add on click function
            )
            self.add_item(self.redirect_to_second_page_button)  # Do not forget to add it to page
            
We’ve now added a button to our page. 
Notice the :code:`create_callable` function used in the :code:`on_click` parameter. The function creates a callable function for the button to use once it’s clicked. 

On click accepts a function name (without brackets) that is executed once the item is clicked. So if we wanted to do some custom action when the button is clicked, we can define our own function::

    def make_some_action():
        # Do stuff
        pass
        
and pass it to the :code:`on_click` parameter::

    self.some_button = Button(
        # parameters
        on_click=make_some_action
    )
    
But what if our function accepts parameters? Thats where the create_callable function comes in handy. It is defined as follows::
    
    def create_callable(func, *args, **kwargs) -> Callable:
    
:code:`create_callable` accepts some function :code:`func`, arguments and key word arguments. It then returns a callable function wich, when called, executes our passed :code:`func` with :code:`*args` and :code:`**kwargs` passed to it.

In above example, where we redirect, the :code:`controller.redirect_to_page` expects a single argument :code:`to_page` (the page we want to redirect to). As we can not pass :code:`controller.redirect_to_page("SecondPage")` as an :code:`on_click` (it executes as we pass it), we use the :code:`create_callable` to pass arguments. 

On another note, if our page accepts parameters in the init method, we can pass those to the :code:`redirect_to_page` method as follows::
    
    create_callable(self.controller.redirect_to_page, "SecondPage", first_argument, second_argument, keyword=argument)
    
Our second page, defined as follows::

    class SecondPage(Page):
        def __init__(self, controller, first_argument, second_argument, keyword=None):
            super().__init__(controller)
            
            # Do something

Will recive those arguments passed with the redirect_to_page method.


Event handlers
==============

You can add your custom event handlers to the main loop, where input and Pygame events are read and handled. Event handlers can be added globaly (via controller object) which apply to every page, or you can add them to one specific page.

Event handlers are made using the :code:`EventHandler` class, where you specify types and handlers. 
Types specify the event type when your handler (a callable function) should be called. 
Types are Pygame specific and you can find a list of them here https://www.pygame.org/docs/ref/event.html
Hanlders are custom functions or methods that must have the :code:`event` parameter, this gets passed automatically once the event type triggers the handler so you can examine different event specific attributes (such as :code:`event.key`). 

We add event handlers to our page by using the :code:`add_event_handler_method` which accepts one event handler object.

Lets add a custom event handler to our :code:`WelcomePage` for executing some action when the space key is clicked::

        import pygame
        from pyggui.gui import Page, EventHandler

        class WelcomePage(Page):
            def __init__(self, controller):
                super().__init__(controller)
                
                self.add_event_handler(
                    event_handler=EventHandler(
                        types=pygame.KEYDOWN,  # Key down event type
                        handlers=self.handle_key_down_event  # Our method defined below
                    )
                )
                 
            def handle_key_down_event(self, event):
                """
                Our custom key down event type handler method.
                """
                if event.key == pygame.K_SPACE:  # If space key was pressed
                    # Do something
                    pass


Above :code:`handle_key_down_event` will be called once any key is pressed. 
Notice the parameters of EventHandler are written as :code:`types` and :code:`handlers`, this is because we can pass it mutliple types and handlers (defined in a list).


Handling files and other helpers
================================

The library also includes functionality for reading different files, directories and other so called "helpers". 

Some of these are::

    DirectoryReader  # For grabbing all files of directories, getting directory structures, ...
    ImageLoader  # For grabbing single images or directories of images loaded into pygame.surface.Surface objects.
    Json  # For loading, saving and updating json files
    create_callable  # We already know about this one
    
These are all imported from the :code:`helpers` package, example::

    from pyggui.helpers import DirectoryReader
    
More info on the helpers documentation TODO: Add link

Custom game loops
=================

Sometimes our games have specific functionalities or just need to be optimized. If you create your whole page system with pyggui and want a custom loop for the actual gameplay 
you can easly create a "Dummy page" and call your main loop function from there.

Every page has an internal :code:`update` and :code:`draw` method. These both get called once every loop for updating and drawing our gui items. 
If you want your custom loop to be executed, you create a dummy page, overwrite either the :code:`update` or :code:`draw` method, call your loop function from there, once your loop finishes (via return) you add a redirection to some other page (such as a StartGame page). If you wish to start your loop you just redirect to this dummy page.

Lets create our custom loop page by overwriting the :code:`update` method of the page and call our :code:`our_custom_loop` function::

    from pyggui.gui import Page
    
    class PlayGameDummyPage(Page):
        def __init__(self, controller):
                super().__init__(controller)
                
        def update(self):  # Overwrite method
            
            our_custom_loop()  # Call your custom loop function
            
            self.controller.redirect_to_page("StartGamePage")  # Redirect to your starting page or some other one once your loop is finished.
            
            # If you do not redirect this will get called in the next loop iteration (almost instantly)




