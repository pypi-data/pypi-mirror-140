from tkinter import *
from tkinter import messagebox
import urllib.request
import pyautogui as pg
import webbrowser as ww
import time as t


# variable declaration
number = ""
txt = ""
loop = 0
clr_fun_lock = 0
abc = 0
a_name = ['Canidae','Felidae', 'Cat', 'Cattle', 'Dog', 'Donkey', 'Goat',
   'Guinea pig', 'Horse', 'Pig', 'Rabbit', 'Fancy rat varieties',
   'laboratory rat strains', 'Sheep breeds', 'Water buffalo breeds',
   'Chicken breeds', 'Duck breeds', 'Goose breeds', 'Pigeon breeds',
   'Turkey breeds', 'Aardvark', 'Aardwolf', 'African buffalo', 'African elephant',
   'African leopard', 'Albatross', 'Alligator', 'Alpaca', 'American buffalo (bison)',
   'American robin', 'Amphibian', 'list', 'Anaconda', 'Angelfish', 'Anglerfish',
   'Ant', 'Anteater', 'Antelope', 'Antlion', 'Ape', 'Aphid', 'Arabian leopard',
   'Arctic Fox', 'Arctic Wolf', 'Armadillo', 'Arrow crab', 'Asp', 'Ass (donkey)',
   'Baboon', 'Badger', 'Bald eagle', 'Bandicoot', 'Barnacle', 'Barracuda', 'Basilisk',
   'Bass', 'Bat', 'Beaked whale', 'Bear', 'list', 'Beaver', 'Bedbug', 'Bee', 'Beetle',
   'Bird', 'list', 'Bison', 'Blackbird', 'Black panther', 'Black widow spider',
   'Blue bird', 'Blue jay', 'Blue whale', 'Boa', 'Boar', 'Bobcat', 'Bobolink',
   'Bonobo', 'Booby', 'Box jellyfish', 'Bovid', 'Buffalo, African', 'Buffalo, American',
   'Bug', 'Butterfly', 'Buzzard', 'Camel', 'Canid', 'Cape buffalo', 'Capybara', 'Cardinal',
   'Caribou', 'Carp', 'Cat', 'list', 'Catshark', 'Caterpillar', 'Catfish', 'Cattle', 'list',
   'Centipede', 'Cephalopod', 'Chameleon', 'Cheetah', 'Chickadee', 'Chicken', 'list',
   'Chimpanzee', 'Chinchilla', 'Chipmunk', 'Clam', 'Clownfish', 'Cobra', 'Cockroach', 'Cod',
   'Condor', 'Constrictor', 'Coral', 'Cougar', 'Cow', 'Coyote', 'Crab', 'Crane', 'Crane fly',
   'Crawdad', 'Crayfish', 'Cricket', 'Crocodile', 'Crow', 'Cuckoo', 'Cicada', 'Damselfly',
   'Deer', 'Dingo', 'Dinosaur', 'list', 'Dog', 'list', 'Dolphin', 'Donkey', 'list', 'Dormouse',
   'Dove', 'Dragonfly', 'Dragon', 'Duck', 'list', 'Dung beetle', 'Eagle', 'Earthworm',
   'Earwig', 'Echidna', 'Eel', 'Egret', 'Elephant', 'Elephant seal', 'Elk', 'Emu',
   'English pointer', 'Ermine', 'Falcon', 'Ferret', 'Finch', 'Firefly', 'Fish', 'Flamingo',
   'Flea', 'Fly', 'Flyingfish', 'Fowl', 'Fox', 'Frog', 'Fruit bat', 'Gamefowl', 'list',
   'Galliform', 'list', 'Gazelle', 'Gecko', 'Gerbil', 'Giant panda', 'Giant squid', 'Gibbon',
   'Gila monster', 'Giraffe', 'Goat', 'list', 'Goldfish', 'Goose', 'list', 'Gopher',
   'Gorilla', 'Grasshopper', 'Great blue heron', 'Great white shark', 'Grizzly bear',
   'Ground shark', 'Ground sloth', 'Grouse', 'Guan', 'list', 'Guanaco', 'Guineafowl', 'list',
   'Guinea pig', 'list', 'Gull', 'Guppy', 'Haddock', 'Halibut', 'Hammerhead shark', 'Hamster',
   'Hare', 'Harrier', 'Hawk', 'Hedgehog', 'Hermit crab', 'Heron', 'Herring', 'Hippopotamus',
   'Hookworm', 'Hornet', 'Horse', 'list', 'Hoverfly', 'Hummingbird', 'Humpback whale',
   'Hyena', 'Iguana', 'Impala', 'Irukandji jellyfish', 'Jackal', 'Jaguar', 'Jay',
   'Jellyfish', 'Junglefowl', 'Kangaroo', 'Kangaroo mouse', 'Kangaroo rat', 'Kingfisher',
   'Kite', 'Kiwi', 'Koala', 'Koi', 'Komodo dragon', 'Krill', 'Ladybug', 'Lamprey', 'Landfowl',
   'Land snail', 'Lark', 'Leech', 'Lemming', 'Lemur', 'Leopard', 'Leopon', 'Limpet',
   'Lion', 'Lizard', 'Llama', 'Lobster', 'Locust', 'Loon', 'Louse', 'Lungfish', 'Lynx',
   'Macaw', 'Mackerel', 'Magpie', 'Mammal', 'Manatee', 'Mandrill', 'Manta ray', 'Marlin',
   'Marmoset', 'Marmot', 'Marsupial', 'Marten', 'Mastodon', 'Meadowlark', 'Meerkat',
   'Mink', 'Minnow', 'Mite', 'Mockingbird', 'Mole', 'Mollusk', 'Mongoose', 'Monitor lizard',
   'Monkey', 'Moose', 'Mosquito', 'Moth', 'Mountain goat', 'Mouse', 'Mule', 'Muskox',
   'Narwhal', 'Newt', 'New World quail', 'Nightingale', 'Ocelot', 'Octopus',
   'Old World quail', 'Opossum', 'Orangutan', 'Orca', 'Ostrich', 'Otter', 'Owl', 'Ox',
   'Panda', 'Panther', 'Panthera hybrid', 'Parakeet', 'Parrot', 'Parrotfish', 'Partridge',
   'Peacock', 'Peafowl', 'Pelican', 'Penguin', 'Perch', 'Peregrine falcon', 'Pheasant',
   'Pig', 'Pigeon', 'list', 'Pike', 'Pilot whale', 'Pinniped', 'Piranha', 'Planarian',
   'Platypus', 'Polar bear', 'Pony', 'Porcupine', 'Porpoise', "Portuguese man o' war",
   'Possum', 'Prairie dog', 'Prawn', 'Praying mantis', 'Primate', 'Ptarmigan', 'Puffin',
   'Puma', 'Python', 'Quail', 'Quelea', 'Quokka', 'Rabbit', 'list', 'Raccoon', 'Rainbow trout',
   'Rat', 'Rattlesnake', 'Raven', 'Ray (Batoidea)', 'Ray (Rajiformes)', 'Red panda',
   'Reindeer', 'Reptile', 'Rhinoceros', 'Right whale', 'Roadrunner', 'Rodent', 'Rook',
   'Rooster', 'Roundworm', 'Saber-toothed cat', 'Sailfish', 'Salamander', 'Salmon',
   'Sawfish', 'Scale insect', 'Scallop', 'Scorpion', 'Seahorse', 'Sea lion', 'Sea slug',
   'Sea snail', 'Shark', 'list', 'Sheep', 'list', 'Shrew', 'Shrimp', 'Silkworm',
   'Silverfish', 'Skink', 'Skunk', 'Sloth', 'Slug', 'Smelt', 'Snail', 'Snake',
   'list', 'Snipe', 'Snow leopard', 'Sockeye salmon', 'Sole', 'Sparrow', 'Sperm whale',
   'Spider', 'Spider monkey', 'Spoonbill', 'Squid', 'Squirrel', 'Starfish',
   'Star-nosed mole', 'Steelhead trout', 'Stingray', 'Stoat', 'Stork', 'Sturgeon',
   'Sugar glider', 'Swallow', 'Swan', 'Swift', 'Swordfish', 'Swordtail', 'Tahr', 'Takin',
   'Tapir', 'Tarantula', 'Tarsier', 'Tasmanian devil', 'Termite', 'Tern', 'Thrush', 'Tick',
   'Tiger', 'Tiger shark', 'Tiglon', 'Toad', 'Tortoise', 'Toucan', 'Trapdoor spider',
   'Tree frog', 'Trout', 'Tuna', 'Turkey', 'list', 'Turtle', 'Tyrannosaurus', 'Urial',
   'Vampire bat', 'Vampire squid', 'Vicuna', 'Viper', 'Vole', 'Vulture', 'Wallaby', 'Walrus',
   'Wasp', 'Warbler', 'Water Boa', 'Water buffalo', 'Weasel', 'Whale', 'Whippet', 'Whitefish',
   'Whooping crane', 'Wildcat', 'Wildebeest', 'Wildfowl', 'Wolf', 'Wolverine', 'Wombat',
   'Woodpecker', 'Worm', 'Wren', 'Xerinae', 'X-ray fish', 'Yak', 'Yellow perch', 'Zebra',
   'Zebra finch', 'Animals by number of neurons', 'Animals by size', 'Common household pests',
   'Common names of poisonous animals', 'Alpaca', 'Bali cattle', 'Cat', 'Cattle', 'Chicken',
   'Dog', 'Domestic Bactrian camel', 'Domestic canary', 'Domestic dromedary camel', 'Domestic duck',
   'Domestic goat', 'Domestic goose', 'Domestic guineafowl', 'Domestic hedgehog', 'Domestic pig',
   'Domestic pigeon', 'Domestic rabbit', 'Domestic silkmoth', 'Domestic silver fox', 'Domestic turkey',
   'Donkey', 'Fancy mouse', 'Fancy rat', 'Lab rat', 'Ferret', 'Gayal', 'Goldfish', 'Guinea pig',
   'Guppy', 'Horse', 'Koi', 'Llama', 'Ringneck dove', 'Sheep', 'Siamese fighting fish',
   'Society finch', 'Yak', 'Water buffalo'] 
bk = 0
def web_ctrl(number):
    # pg.alert(title="Don't do any action until message send successfully")
    ww.open(f"https://web.whatsapp.com/send?phone={number}&text=")
    t.sleep(20)
    pg.press('f11')
    t.sleep(5)
    x, y = pg.size()
    pg.click((x / 2)+100, y-35)
    pg.hotkey('ctrl', 'alt', 'n')
    t.sleep(1)
    pg.hotkey('ctrl','a')
    t.sleep(1)
    pg.press('backspace')
    t.sleep(1)
    pass

def message_start(txt, loop):
    for i in range(loop):
        pg.typewrite(txt)
        pg.press('Enter')


def animal_message(txt, loop):
    global bk
    for i in a_name:
        bk += 1
        if bk == (loop+1):
            break
        op_txt = txt + " is a " + i
        pg.typewrite(op_txt)
        pg.press('Enter')
    pass

def bomb(cmd):
    global abc
    while cmd == 'start':
        try:
            open("background.png")
            open('critiser.png')
            open('message-bomber.png')
            open('start.png')
            open('whatsapp.ico')
        except FileNotFoundError:
            print("Welcome to whatsbombapp")
            print("Due to first time, getting required files. It takes few seconds")
            img1 = 'background.png'
            url1 = 'https://raw.githubusercontent.com/Raguggg/pywhatsbomb_img/main/background.png'
            urllib.request.urlretrieve(url1, img1)
            img2 = 'critiser.png'
            url2 = 'https://raw.githubusercontent.com/Raguggg/pywhatsbomb_img/main/critiser.png'
            urllib.request.urlretrieve(url2, img2)
            img3 = 'message-bomber.png'
            url3 = 'https://raw.githubusercontent.com/Raguggg/pywhatsbomb_img/main/message-bomber.png'
            urllib.request.urlretrieve(url3, img3)
            img4 = 'start.png'
            url4 = 'https://raw.githubusercontent.com/Raguggg/pywhatsbomb_img/main/start.png'
            urllib.request.urlretrieve(url4, img4)
            img5 = 'whatsapp.ico'
            url5 = 'https://icon-icons.com/downloadimage.php?id=37229&root=373/ICO/256/&file=Whatsapp_37229.ico'
            urllib.request.urlretrieve(url5, img5)
            print("...............Hello User.................")
        if abc == 1:
            break

        # Message bomber start function

        def start_mess_bom():
            global number, loop, txt
            if clr_fun_lock >= 1:
                if number.get() == '' or txt.get() == "" or loop.get() == "":
                    messagebox.showwarning("Input Required", "Need still some input")
                    pass
                else:
                    number = number.get()
                    txt = txt.get()
                    loop = int(loop.get())
                    messagebox.showinfo("Alert", 'The message will send in 30 seconds.'
                                                 '\nDon\'t do any action until message send')
                    win.destroy()
                    web_ctrl(number)
                    message_start(txt, loop)
                    pass

            else:
                messagebox.showwarning("Invalid Input", "No input is given")
            pass

        # animals message function

        def critiser_fun():
            global number, loop, txt
            if clr_fun_lock >= 1:
                if number.get() == '' or txt.get() == "" or loop.get() == "":
                    messagebox.showwarning("Input Required", "Need still some input")
                    pass
                else:
                    number = number.get()
                    txt = txt.get()
                    loop = int(loop.get())
                    messagebox.showinfo("Alert", 'The message will send in 30 seconds.'
                                                 '\nDon\'t do any action until message send')
                    win.destroy()
                    web_ctrl(number)
                    animal_message(txt, loop)
                    pass

            else:
                messagebox.showwarning("Invalid Input", "No input is given")
            pass

        # window start program

        win = Tk()
        win.geometry("792x480")
        win.title("Whatsapp bomber .......")
        win.iconbitmap("whatsapp.ico")
        win.resizable(height="false", width="false")
        bg = PhotoImage(file='background.png')
        message_bomb = PhotoImage(file='message-bomber.png')
        critiser = PhotoImage(file='critiser.png')
        start = PhotoImage(file='start.png')
        can = Canvas(win, width=792, height=480)
        can.pack(fill="both", expand=True)
        can.create_image(0, 0, image=bg, anchor="nw")
        text_1 = can.create_text(399, 40, text="Whatsapp Bomber", font=("times", 32), fill="black")
        text_2 = can.create_text(400, 41, text="Whatsapp Bomber", font=("times", 30, 'bold'), fill="White")

        # message bomber button def....
        def mess_bomb():
            global number, txt, loop
            button1.destroy()
            button2.destroy()
            can.delete(text_1, text_2)

            # clear function for temp text

            def clr(e):
                global clr_fun_lock
                clr_fun_lock += 1
                if (number.get() == "+912111111111" and
                         txt.get() == "Hi to Python" and
                         loop.get() == "10") or (number.get() == '+917598226670'):
                    number.delete(0, END)
                    txt.delete(0, END)
                    loop.delete(0, END)
                    number.configure(fg='red')
                    txt.configure(fg='red')
                    loop.configure(fg='red')
                    pass
                pass

            pass

            # window of message bomber
            can.create_text(400, 41, text="Message Bomber", font=("times", 30, 'bold'), fill="White")
            can.create_text(160, 150, text="   Enter The \nPhone Number ", font=("times", 17, 'bold'), fill='white')
            number = Entry(win, font=('times', 16), fg="#5f6368")
            can.create_text(160, 230, text="Enter the Message", font=("times", 17, 'bold'), fill='white')
            txt = Entry(win, font=('times', 16), fg="#5f6368")
            can.create_window(300, 210, anchor="nw", window=txt)
            can.create_text(160, 310, text="Enter The No. \n  of times ", font=("times", 17, 'bold'), fill='white')
            loop = Entry(win, font=('times', 16), fg="#5f6368")
            can.create_window(300, 280, anchor="nw", window=loop)
            can.create_window(300, 130, anchor="nw", window=number)
            start_button = Button(win, image=start, borderwidth=0, command=start_mess_bom)
            can.create_window(320, 330, anchor="nw", window=start_button)
            # temp text in entry box
            number.insert(0, "+912111111111")
            txt.insert(0, "Hi to Python")
            loop.insert(0, "10")
            # clear function
            number.bind("<Button-1>", clr)
            txt.bind("<Button-1>", clr)
            loop.bind("<Button-1>", clr)
            pass

        # animal bomb message

        def animal_bomb():
            global number, txt, loop
            button1.destroy()
            button2.destroy()
            can.delete(text_1, text_2)

            # clear function for temp text

            def clr(e):
                global clr_fun_lock
                clr_fun_lock += 1
                if (number.get() == "+912111111111" and
                         txt.get() == "Python" and
                         loop.get() == "1 - 520") or (number.get() == '+917598226670'):
                    number.delete(0, END)
                    txt.delete(0, END)
                    loop.delete(0, END)
                    number.configure(fg='Green')
                    txt.configure(fg='Green')
                    loop.configure(fg='Green')
                    pass
                pass

            pass

            # window of message bomber
            can.create_text(400, 41, text="CriTisEr", font=("times", 30, 'bold'), fill="White")
            can.create_text(160, 150, text="   Enter The \nPhone Number ", font=("times", 17, 'bold'), fill='white')
            number = Entry(win, font=('times', 16), fg="#5f6368")
            can.create_text(160, 230, text="Enter the Name ", font=("times", 17, 'bold'), fill='white')
            txt = Entry(win, font=('times', 16), fg="#5f6368")
            can.create_window(300, 210, anchor="nw", window=txt)
            can.create_text(160, 310, text="Enter The No. \nanimals name ", font=("times", 17, 'bold'), fill='white')
            loop = Entry(win, font=('times', 16), fg="#5f6368")
            can.create_window(300, 280, anchor="nw", window=loop)
            can.create_window(300, 130, anchor="nw", window=number)
            start_button = Button(win, image=start, borderwidth=0, command=critiser_fun)
            can.create_window(320, 330, anchor="nw", window=start_button)
            # temp text in entry box
            number.insert(0, "+912111111111")
            txt.insert(0, "Python")
            loop.insert(0, "1 - 520")
            # clear function
            number.bind("<Button-1>", clr)
            txt.bind("<Button-1>", clr)
            loop.bind("<Button-1>", clr)
            pass

        button1 = Button(win, image=message_bomb, command=mess_bomb)
        b1 = can.create_window(160, 110, anchor="nw", window=button1)
        button2 = Button(win, image=critiser, command=animal_bomb)
        b2 = can.create_window(170, 300, anchor="nw", window=button2, )

        win.mainloop()
        abc = 1
        pass
    else:
        print('.......invalid......')



#bomb('start')



