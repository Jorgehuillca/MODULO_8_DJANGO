import nodemailer from "nodemailer";

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: "60861853campos@gmail.com",
    pass: "koqt adfu eeiy tjjf"
  }
});

const mailOptions = {
  from: "60861853campos@gmail.com",
  to: "60861853campos@gmail.com",
  subject: "Prueba Gmail desde Node.js",
  text: "Si ves esto, tu Gmail funciona correctamente."
};

transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    return console.error("Error:", error);
  }
  console.log("Correo enviado:", info.response);
});
