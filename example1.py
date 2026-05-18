import threading


class LojaOnline:
    def __init__(self):
        self.estoque = {"item_raro": 1}
        self.mutex = threading.Lock()

    def comprar_item(self, usuario):
        with self.mutex:
            print(f"{usuario} quer comprar o item_raro.")

            if self.estoque["item_raro"] <= 0:
                print(f"{usuario}: Estoque esgotado!")
                return False

            self.estoque["item_raro"] -= 1
            print(
                f"{usuario} comprou com sucesso! "
                f"Estoque restante: {self.estoque['item_raro']}"
            )
            return True


loja = LojaOnline()
usuarios = ["Alice", "Bob", "Carlos"]
threads = []

for usuario in usuarios:
    t = threading.Thread(target=loja.comprar_item, args=(usuario,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
