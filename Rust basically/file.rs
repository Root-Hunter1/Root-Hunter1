fn main() {
    let name = "kimo";
    let mut count = 0;

    for i in 1..=3 {
        count += i;
        println!("step {}: {}, Grand total: {}", i, name, count);
    }
}
