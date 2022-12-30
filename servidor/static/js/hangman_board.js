function display_sentence(sentence) 
{
    sentence_display = "";
    for(let i = 0; i < sentence.length; i++)
    {
        if(sentence[i] == ' ')
        {
            sentence_display += "&nbsp;";
        }
        else
        {
            sentence_display += sentence[i] + "&nbsp;";
        }
    }
}