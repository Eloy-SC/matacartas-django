import os
import unittest

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


FRONTEND_BASE_URL = os.getenv("SELENIUM_FRONTEND_BASE_URL", "http://localhost:5173")
DEFAULT_TIMEOUT = int(os.getenv("SELENIUM_TIMEOUT_SECONDS", "20"))


class FrontendSeleniumBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = Options()
        if os.getenv("SELENIUM_HEADLESS", "1") != "0":
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1600,1200")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        cls.driver = webdriver.Chrome(options=options)
        cls.driver.set_page_load_timeout(DEFAULT_TIMEOUT)
        cls.wait = WebDriverWait(cls.driver, DEFAULT_TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def open(self, path):
        self.driver.get(f"{FRONTEND_BASE_URL}{path}")

    def wait_for(self, by, value):
        return self.wait.until(EC.visibility_of_element_located((by, value)))

    def click(self, by, value):
        element = self.wait_for(by, value)
        element.click()
        return element

    def login_ui(self, username="cervantes", password="123456"):
        self.open("/login")
        self.wait_for(By.ID, "username")
        self.driver.find_element(By.ID, "username").clear()
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.click(By.XPATH, "//button[normalize-space()='Entrar']")
        self.wait.until(EC.url_contains("/inicio"))

    def login_as_admin(self):
        self.login_ui("admin", "123456")


class PublicFrontendSmokeTests(FrontendSeleniumBase):
    def test_home_page_links_to_login_and_register(self):
        self.open("/")

        self.wait_for(By.XPATH, "//button[normalize-space()='INICIA SESIÓN']")
        self.wait_for(By.XPATH, "//button[normalize-space()='REGÍSTRATE']")

        self.click(By.XPATH, "//button[normalize-space()='INICIA SESIÓN']")
        self.wait.until(EC.url_contains("/login"))
        self.wait_for(By.XPATH, "//h2[normalize-space()='INICIO DE SESIÓN']")

        self.driver.back()
        self.wait.until(EC.url_to_be(f"{FRONTEND_BASE_URL}/"))
        self.click(By.XPATH, "//button[normalize-space()='REGÍSTRATE']")
        self.wait.until(EC.url_contains("/login?mode=register"))
        self.wait_for(By.XPATH, "//h2[normalize-space()='REGISTRO']")

    def test_login_register_mode_renders_expected_fields(self):
        self.open("/login?mode=register")

        self.wait_for(By.XPATH, "//h2[normalize-space()='REGISTRO']")
        self.wait_for(By.ID, "nombre")
        self.wait_for(By.ID, "email")
        self.wait_for(By.ID, "repeatPassword")
        self.wait_for(By.ID, "imgUrl")

        self.click(By.XPATH, "//button[normalize-space()='Volver a login']")
        self.wait_for(By.XPATH, "//h2[normalize-space()='INICIO DE SESIÓN']")


class AuthenticatedFrontendSmokeTests(FrontendSeleniumBase):
    def test_inicio_and_perfil_render_after_login(self):
        self.login_ui()

        self.wait_for(By.XPATH, "//img[@alt='Matacartas']")
        self.wait_for(By.XPATH, "//button[@aria-label='Ir al perfil']")
        self.wait_for(By.XPATH, "//button[@aria-label='Ver clasificación']")

        self.click(By.XPATH, "//button[@aria-label='Ir al perfil']")
        self.wait.until(EC.url_contains("/perfil"))
        self.wait_for(By.XPATH, "//h1[normalize-space()='PERFIL']")
        self.wait_for(By.ID, "perfil-username")
        self.wait_for(By.ID, "perfil-email")
        self.wait_for(By.ID, "perfil-nombre")

        self.click(By.XPATH, "//button[normalize-space()='Editar']")
        self.wait_for(By.ID, "perfil-pass1")
        self.wait_for(By.ID, "perfil-pass2")

    def test_partidas_list_create_and_waiting_room_render(self):
        self.login_ui()

        self.open("/partidas")
        self.wait_for(By.XPATH, "//input[@aria-label='Buscar partida']")
        self.wait_for(By.XPATH, "//button[normalize-space()='Crear partida']")

        self.click(By.XPATH, "//button[normalize-space()='Crear partida']")
        self.wait.until(EC.url_contains("/crear-partida"))
        self.wait_for(By.XPATH, "//img[@alt='Matacartas']")
        self.wait_for(By.ID, "titulo")
        self.wait_for(By.ID, "jugadores")
        self.wait_for(By.ID, "longitud")

        self.open("/partidas")
        unirse_buttons = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[normalize-space()='Unirse']"))
        )
        unirse_buttons[0].click()
        self.wait.until(EC.url_contains("/partidas/sala-de-espera/"))
        self.wait_for(By.XPATH, "//h1[contains(normalize-space(), 'Sala de espera:')]")
        self.wait_for(By.XPATH, "//button[@aria-label='Marcar como listo']")
        self.wait_for(By.XPATH, "//button[@aria-label='Volver']")


class AdminFrontendSmokeTests(FrontendSeleniumBase):
    def test_admin_overview_and_forms_render(self):
        self.login_as_admin()

        self.open("/admin")
        self.wait_for(By.XPATH, "//h1[normalize-space()='ADMINISTRACIÓN']")
        self.wait_for(By.XPATH, "//button[normalize-space()='USUARIOS']")
        self.wait_for(By.XPATH, "//button[normalize-space()='RANGOS']")

        self.click(By.XPATH, "//button[normalize-space()='USUARIOS']")
        self.wait.until(EC.url_contains("/admin/usuarios"))
        self.wait_for(By.XPATH, "//h1[normalize-space()='ADMINISTRACIÓN - USUARIOS']")
        self.wait_for(By.XPATH, "//input[@aria-label='Buscar usuario']")
        self.wait_for(By.XPATH, "//button[normalize-space()='Crear usuario']")

        self.click(By.XPATH, "//button[normalize-space()='Crear usuario']")
        self.wait.until(EC.url_contains("/admin/usuarios/crear"))
        self.wait_for(By.XPATH, "//h1[contains(normalize-space(), 'ADMINISTRACION - CREAR USUARIO')]")
        self.wait_for(By.ID, "username")
        self.wait_for(By.ID, "nombre")
        self.wait_for(By.ID, "email")
        self.wait_for(By.ID, "isStaff")

        self.open("/admin/rangos")
        self.wait_for(By.XPATH, "//h1[normalize-space()='ADMINISTRACION - RANGOS']")
        self.wait_for(By.XPATH, "//input[@aria-label='Buscar rango']")
        self.wait_for(By.XPATH, "//button[normalize-space()='Crear rango']")

        self.click(By.XPATH, "//button[normalize-space()='Crear rango']")
        self.wait.until(EC.url_contains("/admin/rangos/crear"))
        self.wait_for(By.XPATH, "//h1[contains(normalize-space(), 'ADMINISTRACION - CREAR RANGO')]")
        self.wait_for(By.ID, "nombre")
        self.wait_for(By.ID, "puntosMinimos")
        self.wait_for(By.ID, "puntosMaximos")
        self.wait_for(By.ID, "color")
