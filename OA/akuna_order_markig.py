import json


class Company:
    def __init__(self, name):
        self.name = name
        self.own = 0
        self.total_unfilled_sell = 0
        self.total_unfilled_buy = 0
        self.unfilled_buy = {}  # {order_id: unfilled quantity}
        self.unfilled_sell = {}  # {order_id, unfilled quantity}

    def get_position(self):
        return self.own - self.total_unfilled_sell

    # add an unfilled order to a company
    def add_unfilled_order(self, order_id, side, quantity):
        if side == "BUY":
            self.unfilled_buy[order_id] = quantity
            self.total_unfilled_buy += quantity
        elif side == "SELL":
            self.unfilled_sell[order_id] = quantity
            self.total_unfilled_sell += quantity

    def delete_unfilled_order(self, order_id, side):
        if side == "BUY":
            self.total_unfilled_buy -= self.unfilled_buy.pop(order_id)
        if side == "SELL":
            self.total_unfilled_sell -= self.unfilled_sell.pop(order_id)

    def fill_order(self, order_id, side, remaining_quantity):
        if side == "BUY":
            filled_this_time = self.unfilled_buy[order_id] - remaining_quantity
            self.own += filled_this_time
            self.total_unfilled_buy -= filled_this_time
            # delete unfilled order if it's fully filled
            if remaining_quantity == 0:
                self.unfilled_buy.pop(order_id)
            else:
                self.unfilled_buy[order_id] = remaining_quantity
        if side == "SELL":
            filled_this_time = self.unfilled_sell[order_id] - remaining_quantity
            self.own -= filled_this_time
            self.total_unfilled_sell -= filled_this_time
            # delete unfilled order if it's fully filled
            if remaining_quantity == 0:
                self.unfilled_sell.pop(order_id)
            else:
                self.unfilled_sell[order_id] = remaining_quantity


class MarkingPositionMonitor:
    def __init__(self):
        self.company_dict = {}  # {company_name: Company}
        self.order_dict = {}  # {order_id: (company_name, side)}

    def on_event(self, message):
        msg_dict = json.loads(message)
        order_id = int(msg_dict["order_id"])

        if msg_dict["type"] == "NEW":
            company = self.new_order(order_id, msg_dict)
            return company.get_position()
        elif msg_dict["type"] == "ORDER_REJECT" or msg_dict["type"] == "CANCEL_ACK":
            company = self.order_rej_cancel(order_id)
            return company.get_position()
        elif msg_dict["type"] == "FILL":
            company = self.fill(order_id, msg_dict)
            return company.get_position()
        else:
            (company_name, side) = self.order_dict[order_id]
            company = self.company_dict[company_name]
            return company.get_position()

    # deal with a NEW
    def new_order(self, order_id, msg_dict):
        side = msg_dict["side"]
        quantity = int(msg_dict["quantity"])
        company_name = msg_dict["symbol"]

        if company_name not in self.company_dict:
            self.company_dict[company_name] = Company(company_name)

        company = self.company_dict[company_name]
        company.add_unfilled_order(order_id, side, quantity)
        self.add_order(order_id, company_name, side)

        return company

    # deal with ORDER_REF and CANCEL_ACK
    def order_rej_cancel(self, order_id):
        (company_name, side) = self.order_dict[order_id]
        company = self.company_dict[company_name]
        company.delete_unfilled_order(order_id, side)

        return company

    # deal with FILL
    def fill(self, order_id, msg_dict):
        remaining_quantity = msg_dict["remaining_quantity"]

        (company_name, side) = self.order_dict[order_id]
        company = self.company_dict[company_name]
        company.fill_order(order_id, side, remaining_quantity)

        return company

    # add new order
    def add_order(self, order_id, company_name, side):
        if order_id not in self.order_dict:
            self.order_dict[order_id] = (company_name, side)

    # def delete_order(self, order_id):
    #     if order_id in self.order_dict:
    #         return self.order_dict.pop(order_id)
    #     else:
    #         return None, None


def assert_equal(a, b):
    if a != b:
        print("False! ", a, b)
    else:
        print(a)


def test1():
    print("###### test 1 ########")
    M = MarkingPositionMonitor()
    string = json.dumps({"type": "NEW", "symbol": "IMIMP", "order_id": 1, "side": "SELL", "quantity": 800,
                         "time": "2017-03-15T10:15:10.975187"})
    assert_equal(M.on_event(string), -800)  # 1

    string = json.dumps(
        {"type": "ORDER_REJECT", "order_id": 1, "reason": "SYMBOL_UNKNOWN", "time": "2017-03-15T10:15:10.975332"})
    # print(M.on_event(string)) #0 2
    assert_equal(M.on_event(string), 0)  # 2
    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 2, "side": "BUY", "quantity": 2000,
                         "time": "2017-03-15T10:15:10.975492"})
    # print(M.on_event(string)) #0 3
    assert_equal(M.on_event(string), 0)  # 3

    string = json.dumps({"type": "ORDER_ACK", "order_id": 2, "time": "2017-03-15T10:15:10.975606"})
    # print(M.on_event(string)) #0 4
    assert_equal(M.on_event(string), 0)  # 4

    string = json.dumps({"type": "FILL", "order_id": 2, "filled_quantity": 2000, "remaining_quantity": 0,
                         "time": "2017-03-15T10:15:10.975717"})
    # print(M.on_event(string)) #2000 5
    assert_equal(M.on_event(string), 2000)  # 5

    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 3, "side": "SELL", "quantity": 700,
                         "time": "2017-03-15T10:15:10.975860"})
    # print(M.on_event(string)) #1300 6
    assert_equal(M.on_event(string), 1300)  # 6

    string = json.dumps({"type": "ORDER_ACK", "order_id": 3, "time": "2017-03-15T10:15:10.975966"})
    # print(M.on_event(string)) #1300  7
    assert_equal(M.on_event(string), 1300)  # 7

    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 4, "side": "SELL", "quantity": 1500,
                         "time": "2017-03-15T10:15:10.976067"})
    # print(M.on_event(string)) #-200  8
    assert_equal(M.on_event(string), -200)  # 8

    string = json.dumps({"type": "ORDER_ACK", "order_id": 4, "time": "2017-03-15T10:15:10.976170"})
    # print(M.on_event(string)) #-200  9
    assert_equal(M.on_event(string), -200)  # 9

    string = json.dumps({"type": "CANCEL", "order_id": 3, "time": "2017-03-15T10:15:10.976431"})
    # print(M.on_event(string)) #-200  10
    assert_equal(M.on_event(string), -200)  # 10

    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 5, "side": "SELL", "quantity": 900,
                         "time": "2017-03-15T10:15:10.976536"})
    # print(M.on_event(string)) #-1100  11
    assert_equal(M.on_event(string), -1100)  # 11

    string = json.dumps({"type": "CANCEL_ACK", "order_id": 3, "time": "2017-03-15T10:15:10.976653"})
    # print(M.on_event(string)) #-400 12
    assert_equal(M.on_event(string), -400)  # 12

    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 6, "side": "SELL", "quantity": 800,
                         "time": "2017-03-15T10:15:10.976778"})
    # print(M.on_event(string)) #-1200 13
    assert_equal(M.on_event(string), -1200)  # 13

    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 7, "side": "BUY", "quantity": 1700,
                         "time": "2017-03-15T10:15:10.976893"})
    # print(M.on_event(string)) #-1200 14
    assert_equal(M.on_event(string), -1200)  # 14

    string = json.dumps({"type": "ORDER_ACK", "order_id": 5, "time": "2017-03-15T10:15:10.977002"})
    # print(M.on_event(string)) #-1200 15
    assert_equal(M.on_event(string), -1200)  # 15

    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 8, "side": "SELL", "quantity": 1300,
                         "time": "2017-03-15T10:15:10.977103"})
    # print(M.on_event(string)) #-2500 16
    assert_equal(M.on_event(string), -2500)  # 16

    string = json.dumps({"type": "ORDER_ACK", "order_id": 6, "time": "2017-03-15T10:15:10.977206"})
    # print(M.on_event(string)) #-2500 17
    assert_equal(M.on_event(string), -2500)  # 17

    string = json.dumps({"type": "CANCEL", "order_id": 7, "time": "2017-03-15T10:15:10.977295"})
    # print(M.on_event(string)) #-2500 18
    assert_equal(M.on_event(string), -2500)  # 18

    string = json.dumps({"type": "ORDER_REJECT", "order_id": 7, "reason": "FIRM_RISK_LIMIT_EXCEEDED",
                         "time": "2017-03-15T10:15:10.977395"})
    # print(M.on_event(string)) #-2500 19
    assert_equal(M.on_event(string), -2500)  # 19

    string = json.dumps({"type": "CANCEL", "order_id": 6, "time": "2017-03-15T10:15:10.977515"})
    # print(M.on_event(string)) #-2500 20
    assert_equal(M.on_event(string), -2500)  # 20

    string = json.dumps({"type": "ORDER_REJECT", "order_id": 8, "reason": "FIRM_RISK_LIMIT_EXCEEDED",
                         "time": "2017-03-15T10:15:10.977665"})
    # print(M.on_event(string)) #-1200 21
    assert_equal(M.on_event(string), -1200)  # 21

    # my additional cases
    string = json.dumps({"type": "NEW", "symbol": "SPY", "order_id": 9, "side": "BUY", "quantity": 1000,
                         "time": "2017-03-15T11:15:10.977103"})
    assert_equal(M.on_event(string), -1200)  # 22

    string = json.dumps({"type": "ORDER_ACK", "order_id": 9, "time": "2017-03-15T11:15:10.977206"})
    assert_equal(M.on_event(string), -1200)  # 23

    string = json.dumps({"type": "FILL", "order_id": 9, "filled_quantity": 200, "remaining_quantity": 800,
                         "time": "2017-03-15T11:15:10.975717"})
    assert_equal(M.on_event(string), -1000)  # 24

    string = json.dumps({"type": "FILL", "order_id": 9, "filled_quantity": 1000, "remaining_quantity": 0,
                         "time": "2017-03-15T11:15:10.975717"})
    assert_equal(M.on_event(string), -200)  # 25


def test2():
    print("###### test 2 ########")
    M2 = MarkingPositionMonitor()
    with open("input002.txt", "r") as f1, open("output002.txt", "r") as f2:
        input_file = f1.readlines()
        f1.close()
        output_file = f2.readlines()
        f2.close()

        input_lines = [x.strip() for x in input_file]
        output_lines = [int(x.strip()) for x in output_file]

        for i in range(len(input_lines)):
            assert_equal(M2.on_event(input_lines[i]), output_lines[i])


if __name__ == "__main__":
    # test1()
    test2()
