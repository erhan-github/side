
struct Order {
    id: u64,
    total: f64,
}

impl Order {
    fn new(id: u64) -> Self {
        Self { id, total: 0.0 }
    }

    fn add_item(&mut self, price: f64) {
        self.total += price;
    }
}

fn process_order(order: Order) {
    println!("Processing {}", order.id);
}
