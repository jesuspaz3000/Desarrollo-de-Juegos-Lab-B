using UnityEngine;

public class ScoreZone : MonoBehaviour
{
	[Header("References")]
	public Cup parentCup; // Referencia a la copa padre

	private void Start()
	{
		// Si no se asigna manualmente, buscar la copa en el padre
		if (parentCup == null)
		{
			parentCup = GetComponentInParent<Cup>();
		}
	}	private void OnTriggerEnter2D(Collider2D other)
	{
		// Verificar si el objeto que colisiona es una pelota o cuadrado
		if (other.GetComponent<Ball>() != null || other.GetComponent<Square>() != null)
		{
			Debug.Log("¡Anotación detectada en ScoreZone!");
			
			// SOLO notificar al ScoreManager directamente
			// NO llamar al padre para evitar doble puntuación
			if (ScoreManager.Instance != null)
			{
				ScoreManager.Instance.AddScore();
			}
		}
	}
}
