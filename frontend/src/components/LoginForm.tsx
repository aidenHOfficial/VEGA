import ConditionalButton from "./ConditionalButton";
import InputField from "./InputField"
import { useState } from "react";

export default function LoginForm() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const disabled = ![username, password].every(Boolean);

    return (
        <form className='flex flex-col gap-3'>
            <InputField type='username' id='usernameInput' label='Username' onChange={(e) => setUsername(e.target.value)}/>
            <InputField type='password' id='passwordInput' label="Password" onChange={(e) => setPassword(e.target.value)}/>
            <ConditionalButton disabled={disabled}>Login</ConditionalButton>
        </form>
    )
}