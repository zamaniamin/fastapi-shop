from apps.accounts.services.token import TokenService


class EmailService:
    @classmethod
    def send_verification_email(cls, email):
        """
        As a development OTP will be printed in the terminal
        """
        # TODO how to ensure that email is sent and delivery?

        otp = TokenService.create_otp_token()
        dev_show = f"""\n\n--- Testing OTP: {otp} ---"""
        print(dev_show)

        # email_body = f"""
        #     Subject: Verify your email address
        #
        #     Dear "{email}",
        #     Thank you for registering for an account on [Your Website Name].
        #
        #     To verify your email address and complete your registration, please enter the following code:
        #     {otp}
        #
        #     If you do not verify your email address within 24 hours, your account will be deleted.
        #     Thank you,
        #     The "Fast Store" Team
        #     """
