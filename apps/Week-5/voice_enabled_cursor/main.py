import speech_recognition as sr


def main():
    r = sr.Recognizer()

    r.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            print("Adjusting for noise...")
            r.adjust_for_ambient_noise(source)

            print("Say something!")

            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                print("You didn't start speaking in time")
                return

            print("Processing audio...")
            try:
                sst = r.recognize_google(audio)
                print("You Said: ", sst)
            except sr.UnknownValueError:
                print("Sorry, could not understand audio")

            except sr.RequestError as e:
                print(f"API error: {e}")

    except OSError as e:
        print(f"Microphone not found or not working: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
