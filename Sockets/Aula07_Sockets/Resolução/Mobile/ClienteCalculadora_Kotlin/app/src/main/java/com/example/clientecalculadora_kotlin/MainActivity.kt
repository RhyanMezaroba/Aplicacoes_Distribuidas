package com.example.clientecalculadora_kotlin

import android.content.res.Configuration
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.lifecycle.lifecycleScope
import com.google.android.material.switchmaterial.SwitchMaterial
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.io.PrintWriter
import java.net.InetSocketAddress
import java.net.Socket
import java.nio.charset.StandardCharsets

class MainActivity : AppCompatActivity() {

    private lateinit var edtNum1: EditText
    private lateinit var edtNum2: EditText
    private lateinit var spnOperacao: Spinner
    private lateinit var btnCalcular: Button
    private lateinit var txtResultado: TextView
    private lateinit var switchTheme: SwitchMaterial

    companion object {
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
        switchTheme = findViewById(R.id.switchTheme)

        // Configuração do Tema Escuro/Claro
        configurarControleDeTema()

        btnCalcular.setOnClickListener {
            val sNum1 = edtNum1.text.toString().trim()
            val sNum2 = edtNum2.text.toString().trim()

            if (sNum1.isEmpty() || sNum2.isEmpty()) {
                Toast.makeText(this, "Preencha ambos os números.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val operacao = spnOperacao.selectedItem.toString()
            executarCalculo(operacao, sNum1.toInt(), sNum2.toInt())
        }
    }

    private fun configurarControleDeTema() {
        val currentNightMode = resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK
        val isDarkMode = currentNightMode == Configuration.UI_MODE_NIGHT_YES

        // Define o estado inicial antes de atrelar o listener para não disparar no onCreate
        switchTheme.isChecked = isDarkMode

        switchTheme.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
            } else {
                AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
            }
        }
    }

    private fun executarCalculo(operacao: String, num1: Int, num2: Int) {
        btnCalcular.isEnabled = false
        txtResultado.text = "Processando..."

        lifecycleScope.launch {
            try {
                val resultadoStr = withContext(Dispatchers.IO) {
                    comunicarComServidor(operacao, num1, num2)
                }
                txtResultado.text = resultadoStr
            } catch (e: Exception) {
                txtResultado.text = "Erro: ${e.message}"
            } finally {
                btnCalcular.isEnabled = true
            }
        }
    }

    private fun comunicarComServidor(operacao: String, num1: Int, num2: Int): String {
        val socket = Socket()
        socket.connect(InetSocketAddress(IP_SERVIDOR, PORTA), 3000)

        socket.use { s ->
            s.soTimeout = 5000

            val saida = PrintWriter(OutputStreamWriter(s.getOutputStream(), StandardCharsets.UTF_8), true)
            val entrada = BufferedReader(InputStreamReader(s.getInputStream(), StandardCharsets.UTF_8))

            val jsonReq = JSONObject().apply {
                put("operacao", operacao)
                put("num1", num1)
                put("num2", num2)
            }

            saida.println(jsonReq.toString())

            val linhaResposta = entrada.readLine() ?: throw Exception("Servidor encerrou sem responder.")
            val jsonRes = JSONObject(linhaResposta)

            return if (jsonRes.getString("status") == "SUCESSO") {
                "Resultado: ${jsonRes.getInt("resultado")}"
            } else {
                "Erro Servidor: ${jsonRes.optString("mensagem", "Falha desconhecida")}"
            }
        }
    }
}