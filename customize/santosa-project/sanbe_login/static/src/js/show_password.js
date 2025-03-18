                    function myFunction(event) {
                        const togglePassword = document.querySelector("#togglePassword");
                        const password = document.querySelector("#password");

                        event.preventDefault()
                        const type = password.getAttribute("type") === "password" ? "text" : "password";
                        password.setAttribute("type", type);
                        
                        // toggle the icon
                        event.target.classList.toggle("fa-eye");
                        event.target.classList.toggle("fa-eye-slash");
                    }