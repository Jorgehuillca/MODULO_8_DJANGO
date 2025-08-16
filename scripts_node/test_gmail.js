import nodemailer from "nodemailer"; // eslint-disable-line no-undef

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "60861853campos@gmail.com",
    pass: "koqt adfu eeiy tjjf"
  }
});

const mailOptions = {
  from: "60861853campos@gmail.com",
  to: "jorgehuillcacondori@gmail.com",
  subject: "Prueba Gmail desde Node.js",
  text: "PRUEBA DE FUNCIÓN CON EL CORREO"
};

transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    return console.error("Error:", error);
  }
  console.log("Correo enviado:", info.response);
});

//cd scripts_node

//node test_gmail.js