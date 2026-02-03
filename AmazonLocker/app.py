from AmazonLocker import Locker, LockerSystem, Size, Staff, AuthorizationError

def print_header():
    print("\n" + "=" * 55)
    print("         SMART LOCKER SYSTEM (Mini Project)")
    print("=" * 55)


def print_lockers(system: LockerSystem):
    print("\nLockers:")
    for l in system.lockers:
        status = "EMPTY" if l.is_empty() else "OCCUPIED"
        print(f" - {l.id:>2} | {l.size.value:<6} | {status}")


def print_tokens(system: LockerSystem):
    # accessing protected member only for demo UI
    tokens = list(system._tokens_by_code.values())
    print("\nActive Tokens:")
    if not tokens:
        print(" (none)")
        return

    for t in tokens:
        exp = t.expiration_date.strftime("%Y-%m-%d %H:%M")
        print(f" - {t.code} | Locker={t.compartment.id} | Expires={exp}")


def choose_size() -> Size:
    while True:
        s = input("Enter size (S/M/L): ").strip().upper()
        if s == "S":
            return Size.SMALL
        if s == "M":
            return Size.MEDIUM
        if s == "L":
            return Size.LARGE
        print("Invalid choice. Please enter S, M, or L.")


def staff_login() -> Staff:
    staff_id = input("Enter staff id: ").strip()
    active_str = input("Is staff active? (y/n): ").strip().lower()
    active = active_str == "y"
    return Staff(id=staff_id, active=active)


def main():
    lockers = [
        Locker("A1", Size.SMALL),
        Locker("A2", Size.SMALL),
        Locker("B1", Size.MEDIUM),
        Locker("C1", Size.LARGE),
    ]
    system = LockerSystem(lockers)

    while True:
        print_header()
        print("1) View lockers")
        print("2) View active tokens (demo)")
        print("3) Staff: Insert package")
        print("4) Staff: Open expired packages")
        print("5) Customer: Pick up package")
        print("0) Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            print_lockers(system)

        elif choice == "2":
            print_tokens(system)

        elif choice == "3":
            staff = staff_login()
            size = choose_size()
            try:
                token = system.insert_package_into_locker(staff, size)
                print("\n✅ Package stored successfully.")
                print(f"Token code: {token.code}")
                print(f"Locker: {token.compartment.id}")
                print(f"Expires: {token.expiration_date}")
            except AuthorizationError as e:
                print(f"\n❌ {e}")
            except ValueError as e:
                print(f"\n❌ {e}")

        elif choice == "4":
            staff = staff_login()
            try:
                opened = system.open_expired_packages(staff)
                if not opened:
                    print("\nNo expired packages found.")
                else:
                    print("\nExpired packages cleared from lockers:")
                    for l in opened:
                        print(f" - {l.id}")
            except AuthorizationError as e:
                print(f"\n❌ {e}")

        elif choice == "5":
            token_code = input("Enter token code: ").strip()
            result = system.pick_up_package(token_code)
            if result == "picked_up":
                print("\n✅ Pick up successful.")
            elif result == "token_expired":
                print("\n❌ Token expired. Please contact staff.")
            else:
                print("\n❌ Invalid token.")

        elif choice == "0":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
