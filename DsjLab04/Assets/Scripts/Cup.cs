
using UnityEngine;

public class Cup : MonoBehaviour
{
	[Header("Score Detection")]
	[Tooltip("Zona interior de la copa para detectar anotaciones")]
	public Transform scoreZone; // Zona interior con trigger

	private void Start()
	{
		// Si no se asignó una zona específica, buscar un hijo con trigger
		if (scoreZone == null)
		{
			// Buscar un collider hijo que sea trigger
			foreach (Transform child in transform)
			{
				Collider2D childCollider = child.GetComponent<Collider2D>();
				if (childCollider != null && childCollider.isTrigger)
				{
					scoreZone = child;
					break;
				}
			}
		}
	}

	private void OnTriggerEnter2D(Collider2D other)
	{
		// Si hay una scoreZone definida, NO procesar aquí para evitar doble detección
		if (scoreZone != null)
		{
			return; // Dejar que ScoreZone maneje la detección
		}
		
		// Solo procesar si NO hay scoreZone (detección directa en Cup)
		if (other.GetComponent<Ball>() != null || other.GetComponent<Square>() != null)
		{
			Debug.Log("¡Anotación! Objeto en la copa (detección directa)");
			
			// Notificar al ScoreManager que hubo una anotación
			if (ScoreManager.Instance != null)
			{
				ScoreManager.Instance.AddScore();
			}
		}
	}

	// Si el scoreZone es un objeto hijo separado, también necesita este método
	public void OnChildTriggerEnter(Collider2D other)
	{
		OnTriggerEnter2D(other);
	}
}
