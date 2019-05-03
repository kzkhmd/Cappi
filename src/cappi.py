import apprunner


def main():
    try:
        app = apprunner.AppRunner()
        app.run()
        
    except KeyboardInterrupt:
        print( 'Exit' )


if __name__ == '__main__':
    main()