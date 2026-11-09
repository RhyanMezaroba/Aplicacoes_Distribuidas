package br.com.herculanodebiasi.clientecalculadorakotlin

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.io.PrintWriter
import java.net.Socket
import java.nio.charset.StandardCharsets

class MainActivity : AppCompatActivity() {

    private lateinit var edtNum1: EditText
    private lateinit var edtNum2: EditText
    private lateinit var spnOperacao: Spinner
    private lateinit var btnCalcular: Button
    private lateinit var txtResultado: TextView

    companion object {
        // REGRA DE CONECTIVIDADE:
        // No Emulador Android Studio: 127.0.0.1 mapeia para o localhost do PC hospedeiro.
        // No Smartphone Físico: Substitua pelo IP da sua placa Wi-Fi (ex: "192.168.0.100").
        private const val IP_SERVIDOR = "127.0.0.1"
        private const val PORTA = 9000
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        edtNum1 = findViewById(R.id.edtNum1)
        edtNum2 = findViewById(R.id.edtNum2)
        spnOperacao = findViewById(R.id.spnOperacao)
        btnCalcular = findViewById(R.id.btnCalcular)
        txtResultado = findViewById(R.id.txtResultado)

        btnCalcular.setOnClickListener {
            val s1 = edtNum1.text.toString().trim()
            val s2 = edtNum2.text.toString().trim()

            if (s1.isEmpty() || s2.isEmpty()) {
                Toast.makeText(this, "Informe os dois números.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val operacao = spnOperacao.selectedItem.toString()
            executarCalculo(s1.toInt(), s2.toInt(), operacao)
        }
    }

    private fun executarCalculo(num1: Int, num2: Int, operacao: String) {
        btnCalcular.isEnabled = false
        txtResultado.text = "Calculando..."

        lifecycleScope.launch {
            try {
                val resultadoStr = withContext(Dispatchers.IO) {
                    Socket(IP_SERVIDOR, PORTA).use { socket ->
                        socket.soTimeout = 5000
                        val saida = PrintWriter(OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true)
                        val entrada = BufferedReader(InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8))

                        // Serializa o JSON de requisição
                        val reqJson = JSONObject().apply {
                            put("operacao", operacao)
                            put("num1", num1)
                            put("num2", num2)
                        }

                        // Envia a linha JSON
                        saida.println(reqJson.toString())

                        // Lê a resposta do servidor
                        val linhaResp = entrada.readLine() ?: throw Exception("Resposta nula do servidor.")
                        val respJson = JSONObject(linhaResp)

                        if (respJson.getString("status") == "SUCESSO") {
                            "Resultado: ${respJson.getInt("resultado")}"
                        } else {
                            "Erro: ${respJson.getString("mensagem")}"
                        }
                    }
                }
                txtResultado.text = resultadoStr
            } catch (e: Exception) {
                txtResultado.text = "Falha: ${e.message}"
            } finally {
                btnCalcular.isEnabled = true
            }
        }
    }
}
