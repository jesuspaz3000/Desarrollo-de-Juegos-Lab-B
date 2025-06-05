using UnityEngine;
using TMPro;

public class ScoreManager : MonoBehaviour
{
    #region Singleton class: ScoreManager

    public static ScoreManager Instance;

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
    }

    #endregion

    [Header("UI Components")]
    public TextMeshProUGUI scoreText;
    
    [Header("Score Settings")]
    private int currentScore = 0;
    public int pointsPerGoal = 1;

    void Start()
    {
        UpdateScoreDisplay();
    }

    public void AddScore()
    {
        currentScore += pointsPerGoal;
        UpdateScoreDisplay();
        
        Debug.Log("¡GOOL! Puntuación actual: " + currentScore);
    }

    private void UpdateScoreDisplay()
    {
        if (scoreText != null)
        {
            scoreText.text = currentScore.ToString();
        }
    }

    public void ResetScore()
    {
        currentScore = 0;
        UpdateScoreDisplay();
    }

    public int GetCurrentScore()
    {
        return currentScore;
    }
}
