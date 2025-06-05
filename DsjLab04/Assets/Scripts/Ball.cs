
using UnityEngine;

public class Ball : MonoBehaviour
{
	[HideInInspector] public Rigidbody2D rb;
	[HideInInspector] public CircleCollider2D col;

	[HideInInspector] public Vector3 pos { get { return transform.position; } }

	void Awake ()
	{
		rb = GetComponent<Rigidbody2D> ();
		col = GetComponent<CircleCollider2D> ();
	}

	public void Push (Vector2 force)
	{
		rb.AddForce (force, ForceMode2D.Impulse);
	}

	public void ActivateRb ()
	{
		rb.bodyType = RigidbodyType2D.Dynamic;
	}

	public void DesactivateRb ()
	{
		rb.linearVelocity = Vector3.zero;
		rb.angularVelocity = 0f;
		rb.bodyType = RigidbodyType2D.Kinematic;
	}
}
