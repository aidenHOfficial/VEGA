import ConditionalButton from "./ConditionalButton";
import InputField from "./InputField"
import { useState } from "react";

export default function RegisterForm() {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [passwordConfirmation, setPasswordConfirmation] = useState("");

    const disabled = ![username, password, email, passwordConfirmation].every(Boolean) && password === passwordConfirmation;

    return (
        <form className='flex flex-col gap-3'>
            <InputField type='username' id='usernameInput' label='Username' onChange={(e) => setUsername(e.target.value)}/>
            <InputField type='email' id='emailInput' label='Email' onChange={(e) => setEmail(e.target.value)}/>
            <InputField type='password' id='passwordInput' label="Password" onChange={(e) => setPassword(e.target.value)}/>
            <InputField type='password' id='passwordConfirmationInput' label='Password Confirmation' onChange={(e) => setPasswordConfirmation(e.target.value)}/>
            <ConditionalButton disabled={disabled}>Register</ConditionalButton>
        </form>
    )
}