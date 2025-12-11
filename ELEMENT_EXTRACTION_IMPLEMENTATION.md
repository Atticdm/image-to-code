# Реализация извлечения элементов дизайна

## ✅ Что уже сделано:

### 1. Backend модули:
- ✅ `backend/image_analysis/element_extraction.py` - извлечение элементов с координатами
- ✅ `backend/image_analysis/svg_extraction.py` - вырезание элементов в SVG через Gemini 3 Pro Image
- ✅ `backend/image_analysis/__init__.py` - экспорт функций
- ✅ `backend/prompts/element_based_prompts.py` - промпты для использования вырезанных элементов

### 2. Frontend типы:
- ✅ Добавлено поле `analysisModel` в `Settings` интерфейс
- ✅ Добавлено поле `useElementExtraction` в параметры генерации

### 3. Структура данных:
- ✅ `ExtractedParams` обновлен для поддержки `analysis_model` и `use_element_extraction`
- ✅ `PipelineContext` обновлен для хранения `extracted_elements` и `element_svgs`

## 🔧 Что нужно доделать:

### 1. Восстановить `backend/routes/generate_code.py`
Файл был поврежден. Нужно:
```bash
git checkout HEAD -- backend/routes/generate_code.py
```

Затем добавить:
- Импорты для `image_analysis` модулей
- `ImageAnalysisStage` класс (уже создан, но нужно правильно вставить)
- Обновить `ExtractedParams` для поддержки новых полей
- Обновить `ParameterExtractionStage` для извлечения `analysisModel`
- Обновить `PromptCreationStage` для использования element-based промптов
- Интегрировать `ImageAnalysisStage` в pipeline

### 2. Обновить UI для выбора модели анализа

В `frontend/src/components/settings/SettingsDialog.tsx` добавить:
```tsx
<div>
  <Label htmlFor="analysis-model">
    <div>Analysis Model (for element extraction)</div>
    <div className="font-light mt-1 text-xs">
      Model used to analyze image and extract design elements
    </div>
  </Label>
  <Select
    value={settings.analysisModel || ""}
    onValueChange={(value) =>
      setSettings((s) => ({
        ...s,
        analysisModel: value as CodeGenerationModel,
      }))
    }
  >
    <SelectTrigger>
      {settings.analysisModel 
        ? CODE_GENERATION_MODEL_DESCRIPTIONS[settings.analysisModel].name
        : "Select model"}
    </SelectTrigger>
    <SelectContent>
      {Object.values(CodeGenerationModel).map((model) => (
        <SelectItem key={model} value={model}>
          {CODE_GENERATION_MODEL_DESCRIPTIONS[model].name}
        </SelectItem>
      ))}
    </SelectContent>
  </Select>
</div>
```

### 3. Обновить `generateCode.ts`

Добавить `analysisModel` в параметры отправки:
```typescript
ws.send(JSON.stringify({
  ...params,
  analysisModel: params.analysisModel || null,
}));
```

### 4. Обновить pipeline в `generate_code.py`

В `CodeGenerationMiddleware.process()` добавить логику:

```python
# Если используется element extraction
if context.extracted_params.use_element_extraction:
    # Этап 1: Анализ изображения и извлечение элементов
    image_analysis_stage = ImageAnalysisStage(
        send_message=context.send_message,
        throw_error=context.throw_error,
    )
    
    image_url = context.extracted_params.prompt["images"][0]
    elements_data, element_svgs = await image_analysis_stage.analyze_image(
        image_data_url=image_url,
        analysis_model=context.extracted_params.analysis_model,
        openai_api_key=context.extracted_params.openai_api_key,
        anthropic_api_key=context.extracted_params.anthropic_api_key,
        gemini_api_key=GEMINI_API_KEY,
    )
    
    # Сохранить в контекст
    context.extracted_elements = elements_data
    context.element_svgs = element_svgs
    
    # Этап 2: Создание промпта с использованием вырезанных элементов
    prompt_stage = PromptCreationStage(context.throw_error)
    prompt_messages, image_cache = await prompt_stage.create_prompt_with_elements(
        extracted_params=context.extracted_params,
        elements_data=elements_data,
        element_svgs=element_svgs,
    )
    context.prompt_messages = prompt_messages
    context.image_cache = element_svgs  # Использовать SVG вместо placeholder
else:
    # Стандартный процесс
    prompt_stage = PromptCreationStage(context.throw_error)
    context.prompt_messages, context.image_cache = await prompt_stage.create_prompt(
        context.extracted_params
    )
```

### 5. Обновить `PromptCreationStage`

Добавить метод `create_prompt_with_elements`:

```python
async def create_prompt_with_elements(
    self,
    extracted_params: ExtractedParams,
    elements_data: Dict[str, Any],
    element_svgs: Dict[str, str],
) -> tuple[List[ChatCompletionMessageParam], Dict[str, str]]:
    """Create prompt using extracted elements"""
    from prompts.element_based_prompts import ELEMENT_BASED_SYSTEM_PROMPTS
    
    stack = extracted_params.stack
    system_content = ELEMENT_BASED_SYSTEM_PROMPTS[stack]
    
    # Добавить информацию об элементах в промпт
    elements_info = json.dumps({
        "elements": elements_data.get("elements", []),
        "image_dimensions": elements_data.get("image_dimensions", {}),
        "element_svgs": element_svgs,
    }, indent=2)
    
    user_content = [
        {
            "type": "image_url",
            "image_url": {"url": extracted_params.prompt["images"][0], "detail": "high"},
        },
        {
            "type": "text",
            "text": f"""Generate code using the extracted design elements.

Extracted elements data:
{elements_info}

Use the provided SVG elements (element_svgs) instead of generating new images.
Place elements at their exact coordinates from the elements data.
""",
        },
    ]
    
    return [
        {
            "role": "system",
            "content": system_content,
        },
        {
            "role": "user",
            "content": user_content,
        },
    ], element_svgs
```

## 📝 Порядок реализации:

1. Восстановить `generate_code.py` из git
2. Добавить импорты и `ImageAnalysisStage` класс
3. Обновить `ExtractedParams` и `ParameterExtractionStage`
4. Обновить `PromptCreationStage` с новым методом
5. Интегрировать в pipeline
6. Обновить UI для выбора модели анализа
7. Обновить frontend для отправки `analysisModel`
8. Протестировать весь процесс

## ⚠️ Важные замечания:

- Gemini API key обязателен для SVG extraction
- Element extraction работает только для `input_mode == "image"` и `generation_type == "create"`
- Если `analysisModel` не указан, используется стандартный процесс
- SVG элементы заменяют placeholder изображения в финальном коде

