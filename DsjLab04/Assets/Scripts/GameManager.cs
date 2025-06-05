using UnityEngine;
using UnityEngine.InputSystem;

public class GameManager : MonoBehaviour
{
    #region Singleton class: GameManager

    public static GameManager Instance;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
    }

    #endregion

    Camera cam;

    public Ball ball;
    public Trajectory trajectory;
    public Square square; // Objeto cuadrado con física
    public ScoreManager scoreManager; // Referencia al ScoreManager
    [SerializeField] float pushForce = 4f;

    bool isDragging = false;
    bool isUsingBall = true; // true = pelota, false = cuadrado

    Vector2 startPoint;
    Vector2 endPoint;
    Vector2 direction;
    Vector2 force;
    float distance;

    //---------------------------------------
    void Start()
    {
        cam = Camera.main;
        ball.DesactivateRb();
        
        // Inicializar el cuadrado si está asignado
        if (square != null)
        {
            square.DesactivateRb(); // Inicialmente sin física
        }
    }

    void Update()
    {
        // Alternar entre pelota y cuadrado con la tecla Espacio
        if (Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame)
        {
            isUsingBall = !isUsingBall;
            Debug.Log("Cambiado a: " + (isUsingBall ? "Pelota" : "Cuadrado"));
        }

        // Resetear puntuación con la tecla R
        if (Keyboard.current != null && Keyboard.current.rKey.wasPressedThisFrame)
        {
            if (scoreManager != null)
            {
                scoreManager.ResetScore();
                Debug.Log("Puntuación reseteada");
            }
        }

        // Usando el nuevo Input System
        if (Mouse.current != null)
        {
            if (Mouse.current.leftButton.wasPressedThisFrame)
            {
                isDragging = true;
                OnDragStart();
            }
            if (Mouse.current.leftButton.wasReleasedThisFrame)
            {
                isDragging = false;
                OnDragEnd();
            }

            if (isDragging)
            {
                OnDrag();
            }
        }
    }

    //-Drag--------------------------------------
    void OnDragStart()
    {
        // Convertir posición del mouse a coordenadas del mundo
        Vector2 mouseWorldPos = cam.ScreenToWorldPoint(Mouse.current.position.ReadValue());
        
        // Verificar sobre qué objeto estamos haciendo clic
        Collider2D hitCollider = Physics2D.OverlapPoint(mouseWorldPos);
        
        bool objectSelected = false;
        
        if (hitCollider != null)
        {
            // Si hacemos clic sobre la pelota
            Ball hitBall = hitCollider.GetComponent<Ball>();
            if (hitBall != null)
            {
                isUsingBall = true;
                ball.DesactivateRb();
                objectSelected = true;
                Debug.Log("Seleccionado por clic: Pelota");
            }
            
            // Si hacemos clic sobre el cuadrado
            Square hitSquare = hitCollider.GetComponent<Square>();
            if (hitSquare != null)
            {
                isUsingBall = false;
                square.DesactivateRb();
                objectSelected = true;
                Debug.Log("Seleccionado por clic: Cuadrado");
            }
        }
        
        // Si no se seleccionó ningún objeto específico, usar el objeto activo actual
        if (!objectSelected)
        {
            if (isUsingBall)
            {
                ball.DesactivateRb();
                Debug.Log("Usando objeto activo: Pelota");
            }
            else
            {
                square.DesactivateRb();
                Debug.Log("Usando objeto activo: Cuadrado");
            }
        }
        
        startPoint = mouseWorldPos;
        trajectory.Show();
    }

    void OnDrag()
    {
        endPoint = cam.ScreenToWorldPoint(Mouse.current.position.ReadValue());
        distance = Vector2.Distance(startPoint, endPoint);
        direction = (startPoint - endPoint).normalized;
        force = direction * distance * pushForce;

        //just for debug
        Debug.DrawLine(startPoint, endPoint);

        // Usar la posición del objeto activo para la trayectoria
        Vector3 activeObjectPos = isUsingBall ? ball.pos : square.pos;
        trajectory.UpdateDots(activeObjectPos, force);
    }

    void OnDragEnd()
    {
        // Activar física y lanzar el objeto activo
        if (isUsingBall)
        {
            ball.ActivateRb();
            ball.Push(force);
        }
        else
        {
            square.ActivateRb();
            square.Push(force);
        }

        trajectory.Hide();
    }
}
