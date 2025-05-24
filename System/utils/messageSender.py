import subprocess
import shlex

class SmsSender:
    def __init__(self, adb_path='adb'):
        self.adb_path = adb_path

    def send_sms(self, phone_number: str, message: str):
        """
        Send SMS by invoking the Android app via ADB shell command.
        Assumes your Android app reads phone_number and message from Intent extras.
        """
        # Escape shell parameters safely
        phone_number_escaped = shlex.quote(phone_number)
        message_escaped = shlex.quote(message)

        # Compose the adb shell am start command with extras to send SMS
        cmd = (
            f"{self.adb_path} shell am start -n com.sentinel.smssender/.MainActivity "
            f"--es phone_number {phone_number_escaped} --es message {message_escaped}"
        )

        try:
            print(f"Executing: {cmd}")
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            print(f"Output:\n{result.stdout}")
            print("SMS command sent successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to send SMS: {e.stderr}")

#if __name__ == "__main__":
#    sender = SmsSender()
#    phone = input("Enter phone number: ")
#    msg = input("Enter message: ")
#    sender.send_sms(phone, msg)
