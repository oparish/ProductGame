# You can place the script of your game in this file.

# Declare images below this line, using the image statement.
# eg. image eileen happy = "eileen_happy.png"

# Declare characters used by this game.
define info = Character('INFO', color="#c8ffc8")

init python:
    import math
    class AmountInput(InputValue):
        def __init__(self, id, amount):
            self.id = id
            self.amount = amount
        def get_text(self):
            return str(self.amount)
        def set_text(self, s):
            if len(s) > 0:
                self.amount = int(s)
            else:
                self.amount = 0
    class Region:
       def __init__(self, data):
           self.id = data['id']
           self.name = data['name']
    class Facility:
        def __init__(self, data):
            self.id = data['id']
            self.type = data['type']
            self.owner = data['owner']
            self.price = data['amount']
            self.name = data['name']
            self.store = [0,0]
            self.import_amount = 10
            self.raid_chance = data['raid_chance']
            self.orig_raid_chance = data['raid_chance']
            self.cool_down = data['cool_down']
            self.cooling = 0
    class Dealer:
        def __init__(self, id, credits, name, routes):
            self.id = id
            self.credits = credits
            self.name = name
            self.routes = routes
            self.revenue = 0
            self.expenses = 0
    class Route:
        def __init__(self, id, resource, amount, source, target):
            self.id = id
            self.resource = resource
            self.amount = amount
            self.source = source
            self.target = target
            self.amountinput = AmountInput(id, amount)
            self.received = 0
    class UI:
        def __init__(self):
            self.details = ""
    class Numbers:
        def __init__(self):
            self.import_rate = 20
            self.production_rate = 20
            self.capacity = 100
            self.distribution_rate = 20
            self.transport_rate = 20
            self.material_price = 2
            self.product_price = 10
    def buy_facility(facility, purchaser):
        purchaser.credits -= facility.price
        facility.owner = purchaser
        renpy.restart_interaction()
    def burn_facility(facility):
        for dealerRoute in facility.owner.routes:
            if dealerRoute.source == facility or dealerRoute.target == facility:
                burn_route(dealerRoute)
        facility.owner = None
        facility.store[0] = 0
        facility.store[1] = 0
        facility.cooling = facility.cool_down
        facility.raid_chance = facility.orig_raid_chance
        renpy.restart_interaction()
    def burn_route(route):
        route.source = None
        route.target = None
    def next_turn():
        while len(messages) > 0 : messages.pop()
        for dealer in dealers:
            bookkeeping(dealer)
        lawmen()
        renpy.restart_interaction()
    def bookkeeping(dealer):
        dealer.revenue = 0
        dealer.expenses = 0
        for route in dealer.routes:
            if route.source != None and route.target != None:
                route.received = min(route.amount, route.source.store[route.resource])
                route.source.store[route.resource] -= route.received
        for facility in facilities:
            if facility.cooling != 0:
                facility.cooling -= 1
        for importer in importers:
            if importer.owner == dealer:
                dealer.expenses += importer.import_amount*NumbersStore.material_price
                importer.store[0] += importer.import_amount
        for producer in producers:
            if producer.owner == dealer:
                amount_produced = min(producer.store[0], NumbersStore.production_rate)
                producer.store[0] -= amount_produced
                producer.store[1] += amount_produced
                if producer.store[1] > NumbersStore.capacity:
                    producer.store[1] = NumbersStore.capacity
        for distributor in distributors:
            if distributor.owner == dealer:
                amount_distributed = min(distributor.store[1], NumbersStore.distribution_rate)
                distributor.store[1] -= amount_distributed
                dealer.revenue += amount_distributed * NumbersStore.product_price
        for route in dealer.routes:
            if route.source != None and route.target != None:
                route.target.store[route.resource] += route.received
                if route.target.store[route.resource] > NumbersStore.capacity:
                    route.target.store[route.resource] = NumbersStore.capacity
        dealer.credits += dealer.revenue
        dealer.credits -= dealer.expenses
    def lawmen():
        for facility in facilities:
            if facility.owner != None and roll(facility.raid_chance):
                raid(facility)
        for facility in facilities:
            if facility.owner != None and roll(20):
                investigate(facility)
    def raid(facility):
        messages.append(facility.name + " raided!")
        burn_facility(facility)
    def investigate(facility):
        messages.append(facility.name + " investigated!")
        facility.raid_chance += 100
    def roll(chance):
        number = renpy.random.randint(0,99)
        if (number < chance):
            return True
        else:
            return False
    def facility_button_name(owner):
        if owner == None:
            return "Unoccupied"
        else:
            return owner.name
    def press_facility_details(facility):
        UIscreen.details = "Material:%d Product:%d"%(facility.store[0], facility.store[1])
        renpy.restart_interaction()
    def press_facility_buy(facility):
        buy_facility(facility, dealers[0])
        renpy.restart_interaction()
    def press_facility_burn(facility):
        burn_facility(facility)
        renpy.restart_interaction()
    def select_route_source(selected_route, facility):
        selected_route.source = facility
        if facility.type == 0 or facility.type == 1:
            selected_route.resource = 0
        else:
            selected_route.resource = 1
        selected_route.target = None
        renpy.restart_interaction()
    def select_route_target(selected_route, facility):
        selected_route.target = facility
        renpy.restart_interaction()
    def select_route_resource(selected_route, i):
        selected_route.resource = i
        renpy.restart_interaction()
    def get_source_name(selected_route):
        if selected_route.source:
            return selected_route.source.name
        else:
            return ""
    def get_target_name(selected_route):
        if selected_route.target:
            return selected_route.target.name
        else:
            return ""
    def get_rotation(ratio):
        return math.degrees(math.atan(ratio))
    def get_line_length(x,y):
        return math.sqrt(x*x + y*y)
    def get_facility_posx(facility):
        if facility.type == 1 or facility.type == 3:
            return facility.id * facilityWidth * 2 + facilityWidth
        else:
            return facility.id * facilityWidth * 2
    def get_facility_posy(facility):
        return facility.type * facilityHeight
    def player_owns_type(facilities):
        for facility in facilities:
            if facility.owner == dealers[0]:
                return True
        return False
    def is_valid_source(facility):
        if facility.owner != dealers[0]:
            return False
        if facility.type == 0:
            if player_owns_type(producers) or player_owns_type(storers):
                return True
            else:
                return False
        elif facility.type == 1:
            if player_owns_type(producers):
                return True
            else:
                return False
        elif facility.type == 2:
            if player_owns_type(prodStorers) or player_owns_type(distributors):
                return True
            else:
                return False
        elif facility.type == 3:
            if player_owns_type(distributors):
                return True
            else:
                return False
        elif facility.type == 4:
            return False
    def is_valid_target(source, target):
        if target.owner != dealers[0]:
            return False
        if source.type == 0:
            if target.type == 1 or target.type == 2:
                return True
            else:
                return False
        elif source.type == 1:
            if target.type == 2:
                return True
            else:
                return False
        elif source.type == 2:
            if target.type == 3 or target.type == 4:
                return True
            else:
                return False
        elif source.type == 3:
            if target.type == 4:
                return True
            else:
                return False
        elif source.type == 4:
            return False
    def to_hq():
        return [0, None]
 
    xnext_turn = renpy.curry(next_turn)
    xpress_facility_details = renpy.curry(press_facility_details)
    xpress_facility_buy = renpy.curry(press_facility_buy)
    xpress_facility_burn = renpy.curry(press_facility_burn)
    xselect_route_source = renpy.curry(select_route_source)
    xselect_route_target = renpy.curry(select_route_target)
    xselect_route_resource = renpy.curry(select_route_resource)
    xhq = renpy.curry(to_hq)
    regions = [Region({'name': 'Region 1', 'id': 1})]
    importers = [Facility({'id': 0, 'type': 0, 'owner': None, 'amount': 10, 'name': "Import 1", 'raid_chance': 10, 'cool_down': 3}), Facility({'id': 1, 'type': 0, 'owner': None, 'amount': 10, 'name': "Import 2", 'raid_chance': 10, 'cool_down': 3}), Facility({'id': 2, 'type': 0, 'owner': None, 'amount': 10, 'name': "Import 3", 'raid_chance': 10, 'cool_down': 3})]
    producers = [Facility({'id': 0, 'type': 2, 'owner': None, 'amount': 10, 'name': "Production 1", 'raid_chance': 10, 'cool_down': 3}), Facility({'id': 1, 'type': 2, 'owner': None, 'amount': 10, 'name': "Production 2", 'raid_chance': 10, 'cool_down': 3})]
    distributors = [Facility({'id': 0, 'type': 4, 'owner': None, 'amount': 10, 'name': "Distributor 1", 'raid_chance': 10, 'cool_down': 3})]
    storers = [Facility({'id': 0, 'type': 1, 'owner': None, 'amount': 10, 'name': "Storage 1", 'raid_chance': 10, 'cool_down': 3})]
    prodStorers = [Facility({'id': 0, 'type': 3, 'owner': None, 'amount': 10, 'name': "Product Storage 1", 'raid_chance': 10, 'cool_down': 3})]
    facilities = importers + producers + distributors + storers + prodStorers
    dealers = [Dealer(0, 1000, "Player", [Route(0, 0, 20, None, None), Route(1, 1, 20, None, None), Route(2, -1, 20, None, None), Route(3, -1, 20, None, None), Route(4, -1, 20, None, None)]), Dealer(1, 200, "Enemy", [])]
    types = ["Import", "Production", "Distribution", "Material Storage", "Product Storage"]
    line_images = ["blueline.png", "redline.png", "greenline.png", "magentaline.png", "cyanline.png"]
    routeCols = ["#0000ff", "#ff0000", "#00ff00", "#ff00ff", "#00ffff"]
    nav = [0]
    textFontSize = 15
    facilityHeight = 130
    facilityWidth = 160
    messages = []
    total_cols = max(len(importers)*2-1,len(storers)*2,len(producers)*2-1,len(prodStorers)*2,len(distributors)*2-1)
    NumbersStore = Numbers()
    UIscreen = UI()

init:
    $ config.keymap['rollforward'] = ['K_PAGEDOWN' ]
    $ config.keymap['rollback'] =  [ 'K_PAGEUP', 'joy_rollback' ]

label start:
    image blueLine = "blueline.png"
    jump main

label main:
    if nav[0] == 1:
        $ nav = renpy.call_screen("assets")
    elif nav[0] == 2:
        $ nav = renpy.call_screen("routes", nav[1])
        if nav[1] != None:
            $ burn_route(nav[1])
    else:
        $ nav = renpy.call_screen("HQ")
    jump main
